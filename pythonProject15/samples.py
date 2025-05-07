import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 设置随机种子
np.random.seed(42)


def generate_courses(num_courses=10):
    # 课程编号
    course_ids = [f'CS{2023000 + i}' for i in range(num_courses)]

    # 课程名称
    course_names = [
        '高级数据结构', '计算机网络', '操作系统', '软件工程', '数据库原理',
        '人工智能', '计算机图形学', '编译原理', '计算机组成原理', '机器学习'
    ]

    # 考试时间
    exam_times = [
        '08:00-10:00', '10:00-12:00', '13:30-15:30', '15:30-17:30', '18:30-20:30',
        '08:00-10:00', '10:00-12:00', '13:30-15:30', '15:30-17:30', '18:30-20:30'
    ]

    # 考试日期
    exam_dates = [
        '2025-05-15', '2025-05-16', '2025-05-17', '2025-05-18', '2025-05-19',
        '2025-05-20', '2025-05-21', '2025-05-22', '2025-05-23', '2025-05-24'
    ]

    # 学历层次
    learning_types = ['本科', '专科', '研究生'] * (num_courses // 3 + 1)

    # 学院
    departments = ['计算机学院', '软件学院', '信息工程学院'] * (num_courses // 3 + 1)

    # 专业
    majors = ['软件工程', '计算机科学', '网络工程', '大数据', '人工智能'] * (num_courses // 5 + 1)

    # 班级
    classes = [f'{major}{"一二三四"[np.random.randint(0, 4)]}班' for major in majors[:num_courses]]

    # 考试地点
    exam_locations = [f'G{np.random.randint(100, 500)}' for _ in range(num_courses)]

    # 教师
    teachers = [f'教师{i}' for i in range(num_courses)]

    # 考试人数
    exam_students_counts = np.random.randint(30, 60, num_courses)

    # 创建DataFrame
    courses_data = {
        '课程编号': course_ids,
        '课程名称': course_names[:num_courses],
        '考试时间': exam_times,
        '考试日期': exam_dates,
        '学历层次': learning_types[:num_courses],
        '任课学院': departments[:num_courses],
        '专业': majors[:num_courses],
        '学院班级': classes,
        '课程名称_重复': course_names[:num_courses],  # 与课程名称相同
        '考试人数': exam_students_counts,
        '考试地点': exam_locations,
        '教师': teachers,
        '周几': np.random.randint(1, 8, num_courses),  # 周几上课
        '节次': np.random.randint(1, 6, num_courses)  # 第几节课
    }

    return pd.DataFrame(courses_data)


# 生成并保存课程表
courses_df = generate_courses()
courses_df.to_excel('courses.xlsx', index=False)
print(courses_df)