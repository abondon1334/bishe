from datetime import datetime, timedelta
from models.database import DatabaseManager

class TeacherConstraintsManager:
    """
    教师约束管理类
    处理教师时间约束、每日考试场次限制等
    """
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager or DatabaseManager()
        
    def validate_teacher_schedule(self, teacher_name, exam_date, exam_time):
        """
        验证教师在指定时间是否可以安排考试
        
        :param teacher_name: 教师姓名
        :param exam_date: 考试日期 (YYYY-MM-DD)
        :param exam_time: 考试时间 (HH:MM-HH:MM)
        :return: (is_valid, reason)
        """
        try:
            # 获取教师约束
            constraints = self.db_manager.get_teacher_constraints(teacher_name)
            
            # 检查每日考试场次限制
            daily_exams = self._get_teacher_daily_exams(teacher_name, exam_date)
            if len(daily_exams) >= constraints['max_exams_per_day']:
                return False, f"教师 {teacher_name} 在 {exam_date} 已安排 {len(daily_exams)} 场考试，超过每日限制 {constraints['max_exams_per_day']} 场"
            
            # 检查晚上考试约束
            if constraints['no_evening_exams'] and self._is_evening_time(exam_time):
                return False, f"教师 {teacher_name} 不接受晚上考试安排"
            
            # 检查周末考试约束
            if constraints['no_weekend_exams'] and self._is_weekend(exam_date):
                return False, f"教师 {teacher_name} 不接受周末考试安排"
            
            # 检查不可用日期
            if exam_date in constraints['unavailable_dates']:
                return False, f"教师 {teacher_name} 在 {exam_date} 不可用"
            
            # 检查不可用时间段
            for unavailable_time in constraints['unavailable_times']:
                if self._time_overlap(exam_time, unavailable_time):
                    return False, f"教师 {teacher_name} 在时间段 {unavailable_time} 不可用"
            
            # 检查时间冲突
            if self._has_time_conflict(teacher_name, exam_date, exam_time):
                return False, f"教师 {teacher_name} 在 {exam_date} {exam_time} 已有其他考试安排"
            
            return True, "可以安排"
            
        except Exception as e:
            return False, f"验证教师时间约束时出错: {e}"
    
    def _get_teacher_daily_exams(self, teacher_name, exam_date):
        """
        获取教师在指定日期的考试安排
        """
        try:
            query = '''
                SELECT ea.考试时间, c.课程名称
                FROM exam_arrangements ea
                JOIN courses c ON ea.教室号 = c.id
                WHERE c.教师 = ? AND ea.考试日期 = ?
            '''
            self.db_manager.cursor.execute(query, (teacher_name, exam_date))
            return self.db_manager.cursor.fetchall()
        except Exception as e:
            print(f"获取教师每日考试安排失败: {e}")
            return []

    def _is_evening_time(self, exam_time):
        """判断是否为晚上时间 (18:30之后)"""
        try:
            start_time = exam_time.split('-')[0].strip()
            hour, minute = map(int, start_time.split(':'))
            return hour >= 18 and minute >= 30  # 修改判断逻辑
        except:
            return False
    
    def _is_weekend(self, exam_date):
        """
        判断是否为周末
        """
        try:
            date_obj = datetime.strptime(exam_date, '%Y-%m-%d')
            return date_obj.weekday() >= 5  # 5=周六, 6=周日
        except:
            return False
    
    def _time_overlap(self, time1, time2):
        """
        检查两个时间段是否重叠
        时间格式: HH:MM-HH:MM
        """
        try:
            def parse_time(time_str):
                start, end = time_str.split('-')
                start_hour, start_min = map(int, start.split(':'))
                end_hour, end_min = map(int, end.split(':'))
                return start_hour * 60 + start_min, end_hour * 60 + end_min
            
            start1, end1 = parse_time(time1)
            start2, end2 = parse_time(time2)
            
            return not (end1 <= start2 or end2 <= start1)
        except:
            return False
    
    def _has_time_conflict(self, teacher_name, exam_date, exam_time):
        """
        检查教师在指定时间是否已有考试安排
        """
        try:
            query = '''
                SELECT COUNT(*)
                FROM exam_arrangements ea
                JOIN courses c ON ea.教室号 = c.id
                WHERE c.教师 = ? AND ea.考试日期 = ? AND ea.考试时间 = ?
            '''
            self.db_manager.cursor.execute(query, (teacher_name, exam_date, exam_time))
            count = self.db_manager.cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            print(f"检查教师时间冲突失败: {e}")
            return True  # 出错时保守处理，认为有冲突
    
    def get_teacher_schedule_summary(self, teacher_name, start_date, end_date):
        """
        获取教师在指定日期范围内的考试安排摘要
        """
        try:
            query = '''
                SELECT ea.考试日期, ea.考试时间, c.课程名称, c.学院班级
                FROM exam_arrangements ea
                JOIN courses c ON ea.教室号 = c.id
                WHERE c.教师 = ? AND ea.考试日期 BETWEEN ? AND ?
                ORDER BY ea.考试日期, ea.考试时间
            '''
            self.db_manager.cursor.execute(query, (teacher_name, start_date, end_date))
            results = self.db_manager.cursor.fetchall()
            
            # 按日期分组
            schedule_by_date = {}
            for result in results:
                date = result[0]
                if date not in schedule_by_date:
                    schedule_by_date[date] = []
                schedule_by_date[date].append({
                    'time': result[1],
                    'course': result[2],
                    'class': result[3]
                })
            
            return schedule_by_date
        except Exception as e:
            print(f"获取教师考试安排摘要失败: {e}")
            return {}
    
    def suggest_alternative_times(self, teacher_name, exam_date, duration_hours=2):
        """
        为教师建议可用的考试时间段
        """
        try:
            # 标准考试时间段
            standard_slots = [
                "08:00-10:00", "10:30-12:30", "14:00-16:00", "16:30-18:30", "19:00-21:00"
            ]
            
            constraints = self.db_manager.get_teacher_constraints(teacher_name)
            available_slots = []
            
            for slot in standard_slots:
                # 检查晚上约束
                if constraints['no_evening_exams'] and self._is_evening_time(slot):
                    continue
                
                # 检查是否可以安排
                is_valid, reason = self.validate_teacher_schedule(teacher_name, exam_date, slot)
                if is_valid:
                    available_slots.append(slot)
            
            return available_slots
        except Exception as e:
            print(f"建议可用时间失败: {e}")
            return [] 