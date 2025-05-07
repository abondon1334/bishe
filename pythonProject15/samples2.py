import pandas as pd
import numpy as np

# 设置随机种子
np.random.seed(42)


def generate_rooms(num_rooms=10):
    # 教室编号
    room_ids = [f'R{2023000 + i}' for i in range(num_rooms)]

    # 教室名称
    room_names = [
        '计算机实验室A', '多媒体教室B', '语言实验室C', '物理实验室D', '化学实验室E',
        '计算机实验室F', '电子实验室G', '生物实验室H', '地理信息实验室I', '机械制图室J'
    ]

    # 教室容量
    capacities = np.random.randint(40, 80, num_rooms)

    # 教学楼
    buildings = ['工程楼', '教学主楼', '实验楼', '科技楼', '综合楼'] * (num_rooms // 5 + 1)

    # 楼层
    floors = np.random.randint(1, 6, num_rooms).astype(str)

    # 可用日期
    available_days = ['1,2,3,4,5'] * num_rooms  # 工作日

    # 可用时间
    available_times = ['08:00-22:00'] * num_rooms

    # 创建DataFrame
    rooms_data = {
        '教室编号': room_ids,
        '教室名称': room_names[:num_rooms],
        '教室容量': capacities,
        '教学楼': buildings[:num_rooms],
        '楼层': floors,
        '可用日期': available_days,
        '可用时间': available_times
    }

    return pd.DataFrame(rooms_data)


# 生成并保存教室配置表
rooms_df = generate_rooms()
rooms_df.to_excel('rooms.xlsx', index=False)
print(rooms_df)