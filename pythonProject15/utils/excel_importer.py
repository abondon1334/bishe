import pandas as pd
import sqlite3

class ExcelImporter:
    def __init__(self, db_path='exam_system.db'):
        self.db_path = db_path

    def import_courses(self, excel_path):
        """
        导入课程数据，过滤掉课程名称为空的记录
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 读取Excel文件
            df = pd.read_excel(excel_path)
            
            # 过滤掉课程名称为空的记录
            df = df.dropna(subset=['课程名称'])
            
            # 删除完全重复的记录（所有字段都相同）
            df = df.drop_duplicates(subset=['课程名称', '时段', '日期', '教室号'], keep='first')
            
            # 删除原有数据
            cursor.execute('DELETE FROM courses')
            
            # 直接使用原始列名插入数据
            for _, row in df.iterrows():
                try:
                    cursor.execute('''
                    INSERT INTO courses (
                        教室号,
                        课程名称,
                        时段,
                        日期,
                        教师类型,
                        任课学院,
                        专业,
                        学院班级,
                        考试人数,
                        考试地点,
                        教师
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        str(row['教室号']),
                        str(row['课程名称']),
                        str(row['时段']),
                        str(row['日期']),
                        str(row['教师类型']),
                        str(row['任课学院']),
                        str(row['专业']),
                        str(row['学院班级']),
                        int(row['考试人数']) if pd.notna(row['考试人数']) else 0,
                        str(row['考试地点']) if pd.notna(row['考试地点']) else '',
                        str(row['教师']) if pd.notna(row['教师']) else ''
                    ))
                except sqlite3.IntegrityError as e:
                    print(f"跳过重复记录: 课程={row['课程名称']}, 时段={row['时段']}, 日期={row['日期']}")
                    continue
            
            conn.commit()
            print(f"成功导入 {len(df)} 条课程记录")
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"导入课程数据出错: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def import_labs(self, excel_path):
        """
        导入教室数据
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 读取Excel文件
            df = pd.read_excel(excel_path)
            
            # 打印原始列名
            print("原始教室配置列名:", df.columns)
            
            # 删除原有数据
            cursor.execute('DELETE FROM exam_rooms')
            
            # 直接使用原始列名插入数据
            for _, row in df.iterrows():
                cursor.execute('''
                INSERT INTO exam_rooms (
                    教室编号, 
                    教室名称, 
                    教室容量, 
                    教学楼,
                    楼层,
                    可用日期,
                    可用时间
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['教室编号'],
                    row['教室名称'],
                    row['教室容量'],
                    row['教学楼'],
                    row['楼层'],
                    row['可用日期'],
                    row['可用时间']
                ))
            
            conn.commit()
            print(f"成功导入 {len(df)} 条教室记录")
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"导入教室数据出错: {e}")
            return False
        finally:
            if conn:
                conn.close() 