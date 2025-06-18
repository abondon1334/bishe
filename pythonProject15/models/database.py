import sqlite3
import hashlib
import random
import os
import pandas as pd
from datetime import datetime


class DatabaseManager:
    def __init__(self, db_path='exam_system.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # 只创建表，不删除已有数据

        # 课程表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            教室号 TEXT NOT NULL,
            课程名称 TEXT NOT NULL,
            时段 TEXT NOT NULL,
            日期 TEXT NOT NULL,
            教师类型 TEXT NOT NULL,
            任课学院 TEXT NOT NULL,
            专业 TEXT NOT NULL,
            学院班级 TEXT NOT NULL,
            考试人数 INTEGER NOT NULL,
            考试地点 TEXT,
            教师 TEXT NOT NULL
        )
        ''')

        # 教室表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS exam_rooms (
            教室编号 TEXT PRIMARY KEY,
            教室名称 TEXT,
            教室容量 INTEGER,
            教学楼 TEXT,
            楼层 TEXT,
            可用日期 TEXT,
            可用时间 TEXT
        )
        ''')

        # 考试安排表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS exam_arrangements (
            arrangement_id INTEGER PRIMARY KEY AUTOINCREMENT,
            教室号 TEXT NOT NULL,
            教室编号 TEXT NOT NULL,
            考试日期 TEXT NOT NULL,
            考试时间 TEXT NOT NULL,
            学院班级 TEXT NOT NULL,
            考试人数 INTEGER NOT NULL,
            任课学院 TEXT NOT NULL,
            专业 TEXT NOT NULL,
            学历层次 TEXT NOT NULL
        )
        ''')

        # 用户表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            name TEXT
        )
        ''')

        # 教师约束表 - 新增
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS teacher_constraints (
            constraint_id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_name TEXT NOT NULL,
            max_exams_per_day INTEGER DEFAULT 3,
             allow_evening_exam INTEGER DEFAULT 1,
            no_evening_exams BOOLEAN DEFAULT 0,
            no_weekend_exams BOOLEAN DEFAULT 0,
            unavailable_dates TEXT,
            unavailable_times TEXT,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(teacher_name)
        )
        ''')

        # 考场调整申请表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS exam_adjustment_requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            arrangement_id INTEGER,  
            申请人 TEXT,
            申请日期 TEXT,
            原考试日期 TEXT,
            原考试时间 TEXT,
            原教室 TEXT,
            新考试日期 TEXT,
            新考试时间 TEXT,
            新教室 TEXT,
            申请理由 TEXT,
            状态 TEXT DEFAULT '待审核',  
            审核人 TEXT,
            审核备注 TEXT,
            FOREIGN KEY(arrangement_id) REFERENCES exam_arrangements(arrangement_id)
        )
        ''')

        # 只在没有管理员用户时创建
        self.cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not self.cursor.fetchone():
            admin_password = self.hash_password('admin123')
            self.cursor.execute('''
            INSERT INTO users (username, password, role, name) 
            VALUES (?, ?, ?, ?)
            ''', ('admin', admin_password, 'admin', '系统管理员'))

        self.conn.commit()

    @staticmethod
    def hash_password(password):
        # 使用SHA-256哈希密码
        return hashlib.sha256(password.encode()).hexdigest()

    def validate_user(self, username, password):
        # 验证用户，不检查角色
        hashed_password = self.hash_password(password)
        self.cursor.execute('''
            SELECT * FROM users 
            WHERE username = ? AND password = ?
        ''', (username, hashed_password))
        return self.cursor.fetchone()

    def add_user(self, username, password, role, name):
        # 添加新用户，默认角色为教师
        hashed_password = self.hash_password(password)
        try:
            self.cursor.execute('''
            INSERT INTO users (username, password, role, name) 
            VALUES (?, ?, ?, ?)
            ''', (username, hashed_password, role, name))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def close(self):
        self.conn.close()

    def import_exam_data(self, exam_data):
        """
        批量导入考试数据
        exam_data: DataFrame或列表，包含考试安排信息
        """
        try:
            # 清空原有数据
            self.cursor.execute('DELETE FROM courses')

            # 打印DataFrame的列名和前几行
            print("课程表列名:", exam_data.columns)
            print("课程表前5行:\n", exam_data.head())

            # 插入课程数据
            for index, row in exam_data.iterrows():
                try:
                    self.cursor.execute('''
                    INSERT INTO courses (
                        course_id, 
                        course_name, 
                        exam_time, 
                        exam_date,
                        learning_type,
                        department,
                        major,
                        class_name,
                        exam_course_name,
                        exam_students_count,
                        exam_location,
                        teacher_name,
                        week_day,
                        time_slot
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        str(row.get('课程编号', '')),
                        str(row.get('课程名称', '')),
                        str(row.get('考试时间', '')),
                        str(row.get('考试日期', '')),
                        str(row.get('学历层次', '')),
                        str(row.get('任课学院', '')),
                        str(row.get('专业', '')),
                        str(row.get('学院班级', '')),
                        str(row.get('课程名称_重复', '')),
                        int(row.get('考试人数', 0)),
                        str(row.get('考试地点', '')),
                        str(row.get('教师', '')),
                        int(row.get('周几', 0)),
                        int(row.get('节次', 0))
                    ))
                except Exception as row_error:
                    print(f"第 {index} 行导入出错: {row_error}")
                    print(f"出错行数据: {row}")

            self.conn.commit()
            return True
        except Exception as e:
            print(f"导入数据出错: {e}")
            self.conn.rollback()
            return False

    def import_rooms_data(self, rooms_data):
        """
        批量导入教室数据
        rooms_data: DataFrame或列表，包含教室配置信息
        """
        try:
            # 清空原有教室数据
            self.cursor.execute('DELETE FROM exam_rooms')

            # 插入教室数据
            for _, row in rooms_data.iterrows():
                self.cursor.execute('''
                INSERT INTO exam_rooms (
                    room_id, 
                    room_name, 
                    capacity,
                    building,
                    floor,
                    available_days,
                    available_times
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(row['教室编号']),
                    str(row['教室名称']),
                    int(row['教室容量']),
                    str(row['教学楼']),
                    str(row['楼层']),
                    str(row['可用日期']),
                    str(row['可用时间'])
                ))

            self.conn.commit()
            return True
        except Exception as e:
            print(f"导入教室数据出错: {e}")
            self.conn.rollback()
            return False

    def auto_arrange_exams(self):
        """
        自动排考场算法
        """
        try:
            # 清空原有考试安排
            self.cursor.execute('DELETE FROM exam_arrangements')

            # 获取所有课程
            self.cursor.execute('SELECT * FROM courses')
            courses = self.cursor.fetchall()
            print("课程总数:", len(courses))

            # 获取所有教室
            self.cursor.execute('SELECT * FROM exam_rooms')
            rooms = self.cursor.fetchall()
            print("教室总数:", len(rooms))

            # 检查数据是否为空
            if not courses:
                print("没有课程数据")
                return False

            if not rooms:
                print("没有教室数据")
                return False

            # 记录已排课的教师和班级，避免冲突
            scheduled_teachers = set()
            scheduled_classes = set()

            for course in courses:
                # 选择合适的教室
                suitable_room = self._find_suitable_room(course, rooms)

                if suitable_room:
                    # 插入考试安排
                    self.cursor.execute('''
                    INSERT INTO exam_arrangements (
                        教室号, 
                        教室编号, 
                        考试日期, 
                        考试时间, 
                        学院班级,
                        考试人数,
                        任课学院,
                        专业,
                        学历层次
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        course[0],  # 教室号
                        suitable_room[0],  # 教室编号
                        course[3],  # 考试日期
                        course[2],  # 考试时间
                        course[7],  # 学院班级
                        course[9],  # 考试人数
                        course[5],  # 任课学院
                        course[6],  # 专业
                        course[4]  # 学历层次
                    ))

            self.conn.commit()
            print("考试安排完成")
            return True
        except Exception as e:
            print(f"自动排考场出错: {e}")
            import traceback
            traceback.print_exc()
            self.conn.rollback()
            return False

    def _find_suitable_room(self, course, rooms):
        """
        选择合适的教室
        """
        try:
            # 打印课程详细信息
            print("课程详细信息:", course)
            print("课程长度:", len(course))

            # 尝试不同的索引获取考试人数
            for i in range(len(course)):
                try:
                    students_count = course[i]
                    print(f"尝试索引 {i}: 人数 = {students_count}")
                except Exception as e:
                    print(f"索引 {i} 出错: {e}")

            # 筛选符合条件的教室
            suitable_rooms = []
            for room in rooms:
                try:
                    # 假设教室容量在索引2的位置
                    if room[2] >= course[9]:
                        suitable_rooms.append(room)
                except Exception as e:
                    print(f"教室匹配出错: {e}")
                    print("教室数据:", room)

            print(f"符合条件的教室: {suitable_rooms}")

            # 如果有多个合适教室，随机选择
            if suitable_rooms:
                selected_room = random.choice(suitable_rooms)
                print(f"选择教室: {selected_room}")
                return selected_room
            else:
                print("没有找到合适的教室")
                return None
        except Exception as e:
            print(f"选择教室出错: {e}")
            print("课程数据:", course)
            return None

    def export_current_exam_arrangements(self, export_path=None):
        """
        导出当前的考试安排到Excel

        :param export_path: 导出路径，默认为用户桌面
        :return: 导出的文件路径
        """
        try:
            # 如果没有指定路径，默认导出到桌面
            if not export_path:
                desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
                export_path = os.path.join(desktop_path, f'考试安排_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')

            # 查询考试安排
            df = pd.read_sql_query('''
                SELECT 
                    c.课程名称, 
                    c.学院班级, 
                    c.教师, 
                    ea.考试日期, 
                    ea.考试时间, 
                    er.教室名称,
                    ea.arrangement_id
                FROM exam_arrangements ea
                JOIN courses c ON ea.教室号 = c.教室号
                JOIN exam_rooms er ON ea.教室编号 = er.教室编号
            ''', self.conn)

            # 导出到Excel
            df.to_excel(export_path, index=False)
            print(f"考试安排已导出到: {export_path}")
            return export_path

        except Exception as e:
            print(f"导出考试安排出错: {e}")
            return None

    def get_teacher_constraints(self, teacher_name):
        """
        获取教师约束信息
        """
        try:
            self.cursor.execute('''
                SELECT max_exams_per_day, no_evening_exams, no_weekend_exams, 
                       unavailable_dates, unavailable_times
                FROM teacher_constraints 
                WHERE teacher_name = ?
            ''', (teacher_name,))
            result = self.cursor.fetchone()

            if result:
                return {
                    'max_exams_per_day': result[0],
                    'no_evening_exams': bool(result[1]),
                    'no_weekend_exams': bool(result[2]),
                    'unavailable_dates': result[3].split(',') if result[3] else [],
                    'unavailable_times': result[4].split(',') if result[4] else []
                }
            else:
                # 返回默认约束
                return {
                    'max_exams_per_day': 3,
                    'no_evening_exams': False,
                    'no_weekend_exams': False,
                    'unavailable_dates': [],
                    'unavailable_times': []
                }
        except Exception as e:
            print(f"获取教师约束失败: {e}")
            return {
                'max_exams_per_day': 3,
                'no_evening_exams': False,
                'no_weekend_exams': False,
                'unavailable_dates': [],
                'unavailable_times': []
            }

    def set_teacher_constraints(self, teacher_name, max_exams_per_day=3,
                                no_evening_exams=False, no_weekend_exams=False,
                                unavailable_dates=None, unavailable_times=None):
        """
        设置教师约束信息
        """
        try:
            unavailable_dates_str = ','.join(unavailable_dates) if unavailable_dates else ''
            unavailable_times_str = ','.join(unavailable_times) if unavailable_times else ''

            self.cursor.execute('''
                INSERT OR REPLACE INTO teacher_constraints 
                (teacher_name, max_exams_per_day, no_evening_exams, no_weekend_exams, 
                 unavailable_dates, unavailable_times)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (teacher_name, max_exams_per_day, no_evening_exams, no_weekend_exams,
                  unavailable_dates_str, unavailable_times_str))

            self.conn.commit()
            return True
        except Exception as e:
            print(f"设置教师约束失败: {e}")
            return False

    def get_exam_arrangements_with_building(self):
        """
        获取包含教学楼信息的考试安排
        """
        try:
            query = '''
                SELECT 
                    c.课程名称, 
                    c.学院班级, 
                    c.教师, 
                    ea.考试日期, 
                    ea.考试时间, 
                    er.教室编号,
                    er.教室名称,
                    er.教学楼,
                    ea.考试人数,
                    ea.arrangement_id
                FROM exam_arrangements ea
                JOIN courses c ON ea.教室号 = c.id
                JOIN exam_rooms er ON ea.教室编号 = er.教室编号
                ORDER BY ea.考试日期, ea.考试时间
            '''

            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"获取考试安排失败: {e}")
            return [] 