#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教师约束初始化脚本
为现有教师设置默认约束：不在晚上考试，不在周末考试
"""

from models.database import DatabaseManager


def init_teacher_constraints():
    """初始化教师约束"""
    print("开始初始化教师约束...")

    db = DatabaseManager()

    try:
        # 获取所有教师
        db.cursor.execute('SELECT DISTINCT 教师 FROM courses WHERE 教师 IS NOT NULL')
        teachers = [row[0] for row in db.cursor.fetchall()]

        print(f'找到 {len(teachers)} 位教师')

        # 为每位教师设置默认约束：不在晚上考试，不在周末考试
        success_count = 0
        for teacher in teachers:
            success = db.set_teacher_constraints(
                teacher_name=teacher,
                max_exams_per_day=3,
                no_evening_exams=True,  # 不在晚上考试
                no_weekend_exams=True,  # 不在周末考试
                unavailable_dates=[],
                unavailable_times=[]
            )
            if success:
                success_count += 1
                print(f'✓ 为教师 {teacher} 设置约束成功')
            else:
                print(f'✗ 为教师 {teacher} 设置约束失败')

        print(f'\n总结：成功为 {success_count}/{len(teachers)} 位教师设置了默认约束')

        # 验证设置结果
        print('\n=== 验证约束设置 ===')
        for teacher in teachers[:5]:  # 只验证前5个
            constraints = db.get_teacher_constraints(teacher)
            print(f'{teacher}: 每日最多{constraints["max_exams_per_day"]}场, '
                  f'不在晚上:{constraints["no_evening_exams"]}, '
                  f'不在周末:{constraints["no_weekend_exams"]}')

        if len(teachers) > 5:
            print(f'... 还有 {len(teachers) - 5} 位教师')

        print('\n初始化完成！教师约束现在应该可以正常工作了。')

    except Exception as e:
        print(f'初始化过程中出现错误: {e}')
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def verify_constraints():
    """验证约束功能是否正常工作"""
    print("\n=== 测试约束功能 ===")

    from utils.teacher_constraints import TeacherConstraintsManager

    db = DatabaseManager()

    try:
        # 获取一个教师进行测试
        db.cursor.execute('SELECT DISTINCT 教师 FROM courses WHERE 教师 IS NOT NULL LIMIT 1')
        result = db.cursor.fetchone()

        if result:
            teacher_name = result[0]
            tcm = TeacherConstraintsManager()

            print(f'测试教师: {teacher_name}')

            # 测试晚上时间约束
            is_valid1, reason1 = tcm.validate_teacher_schedule(teacher_name, '2024-12-20', '19:00-21:00')
            print(f'测试晚上时间约束 (19:00-21:00): {is_valid1}, 原因: {reason1}')

            # 测试周末约束 (2024-12-21是周六)
            is_valid2, reason2 = tcm.validate_teacher_schedule(teacher_name, '2024-12-21', '08:00-10:00')
            print(f'测试周末约束 (周六): {is_valid2}, 原因: {reason2}')

            # 测试正常时间
            is_valid3, reason3 = tcm.validate_teacher_schedule(teacher_name, '2024-12-20', '08:00-10:00')
            print(f'测试正常时间 (周五早上): {is_valid3}, 原因: {reason3}')

            print('\n如果看到上面的约束限制，说明约束功能正常工作！')
        else:
            print('没有找到教师数据')

    except Exception as e:
        print(f'测试过程中出现错误: {e}')
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == '__main__':
    init_teacher_constraints()
    verify_constraints()