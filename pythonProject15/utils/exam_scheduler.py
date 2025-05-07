import sqlite3
import random
from datetime import datetime, timedelta

class ExamScheduler:
    def __init__(self, db_path='exam_system.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        # 默认考试时间段
        self.default_time_slots = [
            "08:00-10:00", "10:30-12:30", "14:00-16:00", "16:30-18:30"
        ]
        # 默认为五场考试时添加的时间段
        self.extra_time_slot = "19:00-21:00"

    def schedule_exams(self, start_date=None, end_date=None, slots_per_day=4):
        """
        自动排考场算法
        根据老师平时上课教室安排考试，处理教室容量和时间冲突问题
        
        :param start_date: 考试开始日期，格式：YYYY-MM-DD
        :param end_date: 考试结束日期，格式：YYYY-MM-DD
        :param slots_per_day: 每天安排的考试场次数量，4或5
        """
        try:
            # 清空原有考试安排
            self.cursor.execute('DELETE FROM exam_arrangements')
            
            # 如果没有指定日期，默认为下周一开始，持续一周
            if not start_date:
                start_date = self._get_next_monday().strftime("%Y-%m-%d")
            if not end_date:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                end_date_obj = start_date_obj + timedelta(days=6)
                end_date = end_date_obj.strftime("%Y-%m-%d")
                
            print(f"排课日期范围: {start_date} 到 {end_date}, 每天 {slots_per_day} 场")
            
            # 设置考试时间段
            time_slots = self.default_time_slots
            if slots_per_day == 5:
                time_slots = time_slots + [self.extra_time_slot]
            
            # 获取所有课程
            self.cursor.execute('''
            SELECT 
                id, 教室号, 课程名称, 时段, 日期, 教师类型, 
                任课学院, 专业, 学院班级, 考试人数, 考试地点, 教师
            FROM courses
            ''')
            courses = self.cursor.fetchall()
            print(f"课程总数: {len(courses)}")

            # 获取所有教室信息
            self.cursor.execute('SELECT 教室编号, 教室名称, 教室容量, 教学楼, 楼层 FROM exam_rooms')
            rooms = self.cursor.fetchall()
            
            # 创建教室字典，方便查询
            room_dict = {room[0]: room for room in rooms}
            
            # 创建教室类型分组，以便在需要更换教室时找到类似类型的教室
            room_types = {}
            for room in rooms:
                room_id, _, _, building, floor = room
                room_type = f"{building}-{floor}"
                if room_type not in room_types:
                    room_types[room_type] = []
                room_types[room_type].append(room_id)
            
            # 记录教室使用情况
            # 格式: {(日期, 时间段, 教室编号): 已用座位数}
            room_usage = {}
            
            # 按教师分组课程，确保同一教师的课程尽量安排在同一教室
            teacher_courses = {}
            for course in courses:
                teacher = course[11]  # 教师
                if teacher not in teacher_courses:
                    teacher_courses[teacher] = []
                teacher_courses[teacher].append(course)
            
            # 生成考试日期安排
            exam_dates = []
            current_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            
            while current_date <= end_date_obj:
                exam_dates.append(current_date.strftime("%Y-%m-%d"))
                current_date += timedelta(days=1)
            
            # 为每个教师的课程安排考试
            for teacher, teacher_course_list in teacher_courses.items():
                # 教师的教室使用记录，用于决定使用哪个教室
                teacher_rooms = {}
                
                # 统计教师使用各教室的次数
                for course in teacher_course_list:
                    room_id = course[1]  # 教室号
                    if room_id not in teacher_rooms:
                        teacher_rooms[room_id] = 0
                    teacher_rooms[room_id] += 1
                
                # 优先使用教师最常用的教室
                preferred_rooms = sorted(teacher_rooms.items(), key=lambda x: x[1], reverse=True)
                
                # 为每个课程安排考试
                for course in teacher_course_list:
                    course_id = course[0]
                    room_id = course[1]  # 原始教室号
                    course_name = course[2]
                    time_slot = course[3]
                    date = course[4]
                    teacher_type = course[5]
                    department = course[6]  # 任课学院
                    major = course[7]  # 专业
                    class_name = course[8]  # 学院班级
                    students_count = course[9]  # 考试人数
                    teacher = course[11]  # 教师
                    
                    # 如果考试人数超过一个合理值（如10人），则使用实际的考试教室
                    actual_students_count = max(10, students_count)
                    
                    # 尝试使用教师常用的教室（按使用频率排序）
                    used_room = False
                    for preferred_room_id, _ in preferred_rooms:
                        # 如果该教室号在room_dict中有对应信息
                        if preferred_room_id in room_dict:
                            room_info = room_dict[preferred_room_id]
                            room_capacity = int(room_info[2])
                            
                            # 如果学生人数超过教室容量，需要分场次考试
                            if actual_students_count > room_capacity:
                                # 计算需要多少场次
                                sessions_needed = (actual_students_count + room_capacity - 1) // room_capacity
                                
                                # 每场安排的学生数量
                                students_per_session = (actual_students_count + sessions_needed - 1) // sessions_needed
                                
                                # 为每场次安排教室和时间
                                for session in range(sessions_needed):
                                    # 分配学生数量
                                    session_students = min(students_per_session, actual_students_count - session * students_per_session)
                                    
                                    # 分配考试日期和时间
                                    assigned = False
                                    
                                    for exam_date in exam_dates:
                                        if assigned:
                                            break
                                            
                                        for time_slot in time_slots:
                                            # 检查该时段该教室是否已被安排
                                            usage_key = (exam_date, time_slot, preferred_room_id)
                                            
                                            if usage_key not in room_usage:
                                                # 安排考试
                                                self._arrange_exam(
                                                    course_id, preferred_room_id, exam_date, time_slot,
                                                    class_name, session_students, department, major, teacher_type,
                                                    teacher, course_name, session + 1, sessions_needed
                                                )
                                                
                                                # 记录教室使用情况
                                                room_usage[usage_key] = session_students
                                                assigned = True
                                                used_room = True
                                                break
                                    
                                    # 如果所有时间段都已安排满，尝试使用同类型的其他教室
                                    if not assigned:
                                        # 获取当前教室的类型
                                        _, _, _, building, floor = room_dict[preferred_room_id]
                                        room_type = f"{building}-{floor}"
                                        
                                        # 查找同类型的其他教室
                                        if room_type in room_types:
                                            for alt_room_id in room_types[room_type]:
                                                if alt_room_id != preferred_room_id:
                                                    # 检查该教室容量是否满足
                                                    alt_room_info = room_dict[alt_room_id]
                                                    alt_room_capacity = int(alt_room_info[2])
                                                    
                                                    if alt_room_capacity >= session_students:
                                                        # 为每个考试日期和时间段检查可用性
                                                        for exam_date in exam_dates:
                                                            if assigned:
                                                                break
                                                                
                                                            for time_slot in time_slots:
                                                                usage_key = (exam_date, time_slot, alt_room_id)
                                                                
                                                                if usage_key not in room_usage:
                                                                    # 安排考试
                                                                    self._arrange_exam(
                                                                        course_id, alt_room_id, exam_date, time_slot,
                                                                        class_name, session_students, department, major, teacher_type,
                                                                        teacher, course_name, session + 1, sessions_needed
                                                                    )
                                                                    
                                                                    # 记录教室使用情况
                                                                    room_usage[usage_key] = session_students
                                                                    assigned = True
                                                                    used_room = True
                                                                    break
                            else:
                                # 学生人数不超过教室容量，直接安排一场考试
                                assigned = False
                                
                                for exam_date in exam_dates:
                                    if assigned:
                                        break
                                        
                                    for time_slot in time_slots:
                                        usage_key = (exam_date, time_slot, preferred_room_id)
                                        
                                        if usage_key not in room_usage:
                                            # 安排考试
                                            self._arrange_exam(
                                                course_id, preferred_room_id, exam_date, time_slot,
                                                class_name, actual_students_count, department, major, teacher_type,
                                                teacher, course_name
                                            )
                                            
                                            # 记录教室使用情况
                                            room_usage[usage_key] = actual_students_count
                                            assigned = True
                                            used_room = True
                                            break
                                
                                # 如果所有时间段都已安排满，尝试使用同类型的其他教室
                                if not assigned:
                                    # 获取当前教室的类型
                                    _, _, _, building, floor = room_dict[preferred_room_id]
                                    room_type = f"{building}-{floor}"
                                    
                                    # 查找同类型的其他教室
                                    if room_type in room_types:
                                        for alt_room_id in room_types[room_type]:
                                            if alt_room_id != preferred_room_id:
                                                # 检查该教室容量是否满足
                                                alt_room_info = room_dict[alt_room_id]
                                                alt_room_capacity = int(alt_room_info[2])
                                                
                                                if alt_room_capacity >= actual_students_count:
                                                    # 为每个考试日期和时间段检查可用性
                                                    for exam_date in exam_dates:
                                                        if assigned:
                                                            break
                                                            
                                                        for time_slot in time_slots:
                                                            usage_key = (exam_date, time_slot, alt_room_id)
                                                            
                                                            if usage_key not in room_usage:
                                                                # 安排考试
                                                                self._arrange_exam(
                                                                    course_id, alt_room_id, exam_date, time_slot,
                                                                    class_name, actual_students_count, department, major, teacher_type,
                                                                    teacher, course_name
                                                                )
                                                                
                                                                # 记录教室使用情况
                                                                room_usage[usage_key] = actual_students_count
                                                                assigned = True
                                                                used_room = True
                                                                break
                        
                        # 如果已成功使用教室，跳出循环
                        if used_room:
                            break
                            
                    # 如果尝试使用教师常用教室失败，随机选择一个符合条件的教室
                    if not used_room:
                        # 为每个可能的日期和时间段检查可用性
                        for exam_date in exam_dates:
                            if used_room:
                                break
                                
                            for time_slot in time_slots:
                                # 查找所有容量符合要求的教室
                                suitable_rooms = [room for room in rooms if int(room[2]) >= actual_students_count]
                                
                                # 随机打乱顺序，避免总是选择同一个教室
                                random.shuffle(suitable_rooms)
                                
                                for room in suitable_rooms:
                                    room_id = room[0]
                                    usage_key = (exam_date, time_slot, room_id)
                                    
                                    if usage_key not in room_usage:
                                        # 安排考试
                                        self._arrange_exam(
                                            course_id, room_id, exam_date, time_slot,
                                            class_name, actual_students_count, department, major, teacher_type,
                                            teacher, course_name
                                        )
                                        
                                        # 记录教室使用情况
                                        room_usage[usage_key] = actual_students_count
                                        used_room = True
                                        break
                                
                                if used_room:
                                    break
            
            # 打印统计信息
            print(f"成功安排 {len(room_usage)} 场考试")
            self.conn.commit()
            return True

        except Exception as e:
            print(f"自动排考场出错: {e}")
            import traceback
            traceback.print_exc()
            self.conn.rollback()
            return False

    def _arrange_exam(self, course_id, room_id, exam_date, exam_time, class_name, 
                     students_count, department, major, teacher_type, teacher, course_name, 
                     session=None, total_sessions=None):
        """
        安排一场考试
        
        :param session: 如果是多场次考试，当前是第几场
        :param total_sessions: 如果是多场次考试，总共有几场
        """
        try:
            # 构建考试场次说明（如果有多场）
            session_info = ""
            if session and total_sessions:
                session_info = f"(第{session}场/共{total_sessions}场)"
            
            # 获取教室名称
            self.cursor.execute('SELECT 教室名称 FROM exam_rooms WHERE 教室编号 = ?', (room_id,))
            room_name_result = self.cursor.fetchone()
            room_name = room_name_result[0] if room_name_result else "未知教室"
            
            # 记录考试安排
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
                course_id,  # 使用课程ID作为教室号字段（原代码使用的逻辑）
                room_id,    # 实际的教室编号
                exam_date,  # 考试日期
                exam_time,  # 考试时间
                class_name, # 学院班级
                students_count, # 考试人数
                department, # 任课学院
                major,      # 专业
                teacher_type # 学历层次
            ))
            
            print(f"安排考试: {course_name} - {teacher} - {room_name} - {exam_date} {exam_time} {session_info}")
            return True
        except Exception as e:
            print(f"安排考试出错: {e}")
            return False

    def _get_next_monday(self):
        # 获取下周一的日期
        today = datetime.now()
        days_until_monday = 7 - today.weekday()
        if days_until_monday == 7:
            days_until_monday = 0  # 如果今天是周一，返回今天
        return today.date() + timedelta(days=days_until_monday)

    def _find_suitable_room(self, students_count, rooms, exam_date, exam_time, scheduled_rooms):
        """
        选择合适的教室，考虑容量和时间冲突
        """
        try:
            suitable_rooms = []
            for room in rooms:
                room_id = room[0]  # 教室编号
                room_capacity = int(room[2])  # 教室容量

                # 检查容量是否满足
                if room_capacity < int(students_count):
                    print(f"教室 {room_id} 容量不足: {room_capacity} < {students_count}")
                    continue
                    
                # 检查该时间段是否已被占用
                if any(key[0] == exam_date and key[1] == exam_time and key[2] == room_id 
                      for key in scheduled_rooms.keys()):
                    print(f"教室 {room_id} 在 {exam_date} {exam_time} 已被占用")
                    continue
                    
                suitable_rooms.append(room)

            if suitable_rooms:
                # 优先选择容量最接近的教室
                suitable_rooms.sort(key=lambda x: int(x[2]) - int(students_count))
                selected_room = suitable_rooms[0]
                print(f"为考试人数 {students_count} 选择教室: {selected_room[1]}(容量:{selected_room[2]})")
                return selected_room
            
            return None
        except Exception as e:
            print(f"选择教室出错: {e}")
            return None

    def adjust_exam_arrangement(self, arrangement_id, new_room_id=None, new_date=None, new_time=None):
        """
        手动调整考试安排
        
        :param arrangement_id: 考试安排的ID
        :param new_room_id: 新的教室编号
        :param new_date: 新的考试日期
        :param new_time: 新的考试时间
        :return: 是否调整成功
        """
        try:
            # 检查参数有效性
            if not arrangement_id:
                print("无效的安排ID")
                return False

            # 准备更新语句
            update_parts = []
            params = []

            if new_room_id:
                update_parts.append("教室编号 = ?")
                params.append(new_room_id)

            if new_date:
                update_parts.append("考试日期 = ?")
                params.append(new_date)

            if new_time:
                update_parts.append("考试时间 = ?")
                params.append(new_time)

            # 如果没有更新项，直接返回
            if not update_parts:
                print("没有需要更新的内容")
                return False

            # 添加条件参数
            params.append(arrangement_id)
            
            # 构建完整的更新语句
            query = f"UPDATE exam_arrangements SET {', '.join(update_parts)} WHERE arrangement_id = ?"
            
            # 执行更新
            self.cursor.execute(query, params)
            self.conn.commit()
            
            print(f"成功调整考试安排 {arrangement_id}")
            return True
        
        except sqlite3.Error as e:
            print(f"调整考试安排出错: {e}")
            self.conn.rollback()
            return False
        except Exception as e:
            print(f"未知错误: {e}")
            self.conn.rollback()
            return False

    def close(self):
        self.conn.close()

    def export_exam_arrangements(self):
        # 导出考试安排
        pass 