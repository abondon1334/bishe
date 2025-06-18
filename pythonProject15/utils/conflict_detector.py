from models.database import DatabaseManager
from datetime import datetime

class ConflictDetector:
    """
    冲突检测工具类
    检测教室、教师、学生的时间冲突
    """
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager or DatabaseManager()
    
    def check_room_conflict(self, room_id, exam_date, exam_time, exclude_arrangement_id=None):
        """
        检查教室时间冲突
        
        :param room_id: 教室编号
        :param exam_date: 考试日期
        :param exam_time: 考试时间
        :param exclude_arrangement_id: 排除的考试安排ID（用于调整时）
        :return: (has_conflict, conflict_info)
        """
        try:
            query = '''
                SELECT ea.arrangement_id, c.课程名称, c.学院班级, c.教师
                FROM exam_arrangements ea
                JOIN courses c ON ea.教室号 = c.id
                WHERE ea.教室编号 = ? AND ea.考试日期 = ? AND ea.考试时间 = ?
            '''
            params = [room_id, exam_date, exam_time]
            
            if exclude_arrangement_id:
                query += ' AND ea.arrangement_id != ?'
                params.append(exclude_arrangement_id)
            
            self.db_manager.cursor.execute(query, params)
            conflicts = self.db_manager.cursor.fetchall()
            
            if conflicts:
                conflict_info = []
                for conflict in conflicts:
                    conflict_info.append({
                        'arrangement_id': conflict[0],
                        'course_name': conflict[1],
                        'class_name': conflict[2],
                        'teacher': conflict[3]
                    })
                return True, conflict_info
            
            return False, []
            
        except Exception as e:
            print(f"检查教室冲突失败: {e}")
            return True, [{'error': str(e)}]  # 出错时保守处理
    
    def check_teacher_conflict(self, teacher_name, exam_date, exam_time, exclude_arrangement_id=None):
        """
        检查教师时间冲突
        """
        try:
            query = '''
                SELECT ea.arrangement_id, c.课程名称, c.学院班级, er.教室名称
                FROM exam_arrangements ea
                JOIN courses c ON ea.教室号 = c.id
                JOIN exam_rooms er ON ea.教室编号 = er.教室编号
                WHERE c.教师 = ? AND ea.考试日期 = ? AND ea.考试时间 = ?
            '''
            params = [teacher_name, exam_date, exam_time]
            
            if exclude_arrangement_id:
                query += ' AND ea.arrangement_id != ?'
                params.append(exclude_arrangement_id)
            
            self.db_manager.cursor.execute(query, params)
            conflicts = self.db_manager.cursor.fetchall()
            
            if conflicts:
                conflict_info = []
                for conflict in conflicts:
                    conflict_info.append({
                        'arrangement_id': conflict[0],
                        'course_name': conflict[1],
                        'class_name': conflict[2],
                        'room_name': conflict[3]
                    })
                return True, conflict_info
            
            return False, []
            
        except Exception as e:
            print(f"检查教师冲突失败: {e}")
            return True, [{'error': str(e)}]
    
    def check_class_conflict(self, class_name, exam_date, exam_time, exclude_arrangement_id=None):
        """
        检查学生班级时间冲突
        """
        try:
            query = '''
                SELECT ea.arrangement_id, c.课程名称, c.教师, er.教室名称
                FROM exam_arrangements ea
                JOIN courses c ON ea.教室号 = c.id
                JOIN exam_rooms er ON ea.教室编号 = er.教室编号
                WHERE c.学院班级 = ? AND ea.考试日期 = ? AND ea.考试时间 = ?
            '''
            params = [class_name, exam_date, exam_time]
            
            if exclude_arrangement_id:
                query += ' AND ea.arrangement_id != ?'
                params.append(exclude_arrangement_id)
            
            self.db_manager.cursor.execute(query, params)
            conflicts = self.db_manager.cursor.fetchall()
            
            if conflicts:
                conflict_info = []
                for conflict in conflicts:
                    conflict_info.append({
                        'arrangement_id': conflict[0],
                        'course_name': conflict[1],
                        'teacher': conflict[2],
                        'room_name': conflict[3]
                    })
                return True, conflict_info
            
            return False, []
            
        except Exception as e:
            print(f"检查班级冲突失败: {e}")
            return True, [{'error': str(e)}]
    
    def check_all_conflicts(self, room_id, teacher_name, class_name, exam_date, exam_time, exclude_arrangement_id=None):
        """
        检查所有类型的冲突
        
        :return: (has_any_conflict, conflict_details)
        """
        all_conflicts = {
            'room_conflicts': [],
            'teacher_conflicts': [],
            'class_conflicts': []
        }
        
        has_any_conflict = False
        
        # 检查教室冲突
        room_conflict, room_info = self.check_room_conflict(room_id, exam_date, exam_time, exclude_arrangement_id)
        if room_conflict:
            has_any_conflict = True
            all_conflicts['room_conflicts'] = room_info
        
        # 检查教师冲突
        teacher_conflict, teacher_info = self.check_teacher_conflict(teacher_name, exam_date, exam_time, exclude_arrangement_id)
        if teacher_conflict:
            has_any_conflict = True
            all_conflicts['teacher_conflicts'] = teacher_info
        
        # 检查班级冲突
        class_conflict, class_info = self.check_class_conflict(class_name, exam_date, exam_time, exclude_arrangement_id)
        if class_conflict:
            has_any_conflict = True
            all_conflicts['class_conflicts'] = class_info
        
        return has_any_conflict, all_conflicts
    
    def format_conflict_message(self, conflicts):
        """
        格式化冲突信息为用户友好的消息
        """
        messages = []
        
        if conflicts['room_conflicts']:
            messages.append("教室冲突:")
            for conflict in conflicts['room_conflicts']:
                if 'error' in conflict:
                    messages.append(f"  - 检查出错: {conflict['error']}")
                else:
                    messages.append(f"  - {conflict['course_name']} ({conflict['class_name']}, 教师: {conflict['teacher']})")
        
        if conflicts['teacher_conflicts']:
            messages.append("教师冲突:")
            for conflict in conflicts['teacher_conflicts']:
                if 'error' in conflict:
                    messages.append(f"  - 检查出错: {conflict['error']}")
                else:
                    messages.append(f"  - {conflict['course_name']} ({conflict['class_name']}, 教室: {conflict['room_name']})")
        
        if conflicts['class_conflicts']:
            messages.append("班级冲突:")
            for conflict in conflicts['class_conflicts']:
                if 'error' in conflict:
                    messages.append(f"  - 检查出错: {conflict['error']}")
                else:
                    messages.append(f"  - {conflict['course_name']} (教师: {conflict['teacher']}, 教室: {conflict['room_name']})")
        
        return "\n".join(messages)
    
    def get_available_rooms(self, exam_date, exam_time, min_capacity=0):
        """
        获取指定时间可用的教室列表
        """
        try:
            # 获取所有教室
            self.db_manager.cursor.execute('''
                SELECT 教室编号, 教室名称, 教室容量, 教学楼
                FROM exam_rooms
                WHERE 教室容量 >= ?
            ''', (min_capacity,))
            all_rooms = self.db_manager.cursor.fetchall()
            
            available_rooms = []
            for room in all_rooms:
                room_id = room[0]
                has_conflict, _ = self.check_room_conflict(room_id, exam_date, exam_time)
                if not has_conflict:
                    available_rooms.append({
                        'room_id': room[0],
                        'room_name': room[1],
                        'capacity': room[2],
                        'building': room[3]
                    })
            
            return available_rooms
            
        except Exception as e:
            print(f"获取可用教室失败: {e}")
            return []
    
    def suggest_alternative_arrangements(self, teacher_name, class_name, exam_date, min_capacity=0):
        """
        为指定教师和班级建议可用的考试安排
        """
        try:
            # 标准考试时间段
            time_slots = [
                "08:00-10:00", "10:30-12:30", "14:00-16:00", "16:30-18:30", "19:00-21:00"
            ]
            
            suggestions = []
            
            for time_slot in time_slots:
                # 检查教师和班级在该时间段是否有冲突
                teacher_conflict, _ = self.check_teacher_conflict(teacher_name, exam_date, time_slot)
                class_conflict, _ = self.check_class_conflict(class_name, exam_date, time_slot)
                
                if not teacher_conflict and not class_conflict:
                    # 获取可用教室
                    available_rooms = self.get_available_rooms(exam_date, time_slot, min_capacity)
                    if available_rooms:
                        suggestions.append({
                            'time': time_slot,
                            'available_rooms': available_rooms
                        })
            
            return suggestions
            
        except Exception as e:
            print(f"建议替代安排失败: {e}")
            return [] 