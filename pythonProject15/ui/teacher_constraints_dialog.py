from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QMessageBox, QHeaderView,
                             QLabel, QGroupBox, QCheckBox, QSpinBox, QFormLayout)
from PyQt5.QtGui import QColor
from models.database import DatabaseManager
from ui.teacher_constraints_dialog import TeacherConstraintsDialog


class TeacherConstraintsManager(QWidget):
    """教师约束管理界面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('教师约束管理')
        self.setMinimumSize(1000, 700)
        self.init_ui()
        self.load_teacher_constraints()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 标题和操作按钮
        header_layout = QHBoxLayout()
        title_label = QLabel("教师约束管理")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        # 操作按钮
        refresh_btn = QPushButton("刷新")
        batch_set_btn = QPushButton("批量设置")
        init_default_btn = QPushButton("初始化默认约束")

        refresh_btn.clicked.connect(self.load_teacher_constraints)
        batch_set_btn.clicked.connect(self.batch_set_constraints)
        init_default_btn.clicked.connect(self.init_default_constraints)

        header_layout.addWidget(refresh_btn)
        header_layout.addWidget(batch_set_btn)
        header_layout.addWidget(init_default_btn)

        layout.addLayout(header_layout)

        # 批量设置区域
        batch_group = QGroupBox("批量设置默认约束")
        batch_layout = QFormLayout()

        # 批量设置选项
        self.batch_max_exams = QSpinBox()
        self.batch_max_exams.setRange(1, 10)
        self.batch_max_exams.setValue(3)
        self.batch_max_exams.setSuffix(" 场")
        batch_layout.addRow("每日最多考试场次:", self.batch_max_exams)

        self.batch_no_evening = QCheckBox("不在晚上考试")
        self.batch_no_evening.setChecked(True)
        batch_layout.addRow(self.batch_no_evening)

        self.batch_no_weekend = QCheckBox("不在周末考试")
        self.batch_no_weekend.setChecked(True)
        batch_layout.addRow(self.batch_no_weekend)

        batch_group.setLayout(batch_layout)
        batch_group.setMaximumHeight(150)
        layout.addWidget(batch_group)

        # 教师约束表格
        self.create_constraints_table()
        layout.addWidget(self.constraints_table)

        # 底部按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        edit_btn = QPushButton("编辑选中教师")
        delete_btn = QPushButton("删除选中约束")

        edit_btn.clicked.connect(self.edit_selected_teacher)
        delete_btn.clicked.connect(self.delete_selected_constraints)

        bottom_layout.addWidget(edit_btn)
        bottom_layout.addWidget(delete_btn)

        layout.addLayout(bottom_layout)

        # 设置样式
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                min-width: 80px;
                min-height: 30px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)

    def create_constraints_table(self):
        """创建约束表格"""
        self.constraints_table = QTableWidget()
        self.constraints_table.setColumnCount(7)
        self.constraints_table.setHorizontalHeaderLabels([
            '教师姓名', '每日最多考试', '不在晚上考试', '不在周末考试',
            '不可用日期数', '不可用时间段数', '最后更新时间'
        ])

        # 设置表格属性
        self.constraints_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.constraints_table.setAlternatingRowColors(True)
        self.constraints_table.setSortingEnabled(True)

        # 调整列宽
        header = self.constraints_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # 教师姓名
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 每日最多考试
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 不在晚上考试
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 不在周末考试
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 不可用日期数
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # 不可用时间段数
        header.setSectionResizeMode(6, QHeaderView.Stretch)  # 最后更新时间

        # 双击编辑
        self.constraints_table.itemDoubleClicked.connect(self.edit_selected_teacher)

    def load_teacher_constraints(self):
        """加载教师约束数据"""
        try:
            db_manager = DatabaseManager()

            # 获取所有教师列表
            db_manager.cursor.execute('SELECT DISTINCT 教师 FROM courses WHERE 教师 IS NOT NULL')
            all_teachers = [row[0] for row in db_manager.cursor.fetchall()]

            # 获取已设置约束的教师
            db_manager.cursor.execute('''
                SELECT teacher_name, max_exams_per_day, no_evening_exams, no_weekend_exams,
                       unavailable_dates, unavailable_times, created_date
                FROM teacher_constraints
                ORDER BY teacher_name
            ''')
            constraints_data = db_manager.cursor.fetchall()

            # 创建约束数据字典
            constraints_dict = {}
            for row in constraints_data:
                teacher_name = row[0]
                unavailable_dates_count = len(row[4].split(',')) if row[4] else 0
                unavailable_times_count = len(row[5].split(',')) if row[5] else 0

                constraints_dict[teacher_name] = {
                    'max_exams_per_day': row[1],
                    'no_evening_exams': bool(row[2]),
                    'no_weekend_exams': bool(row[3]),
                    'unavailable_dates_count': unavailable_dates_count,
                    'unavailable_times_count': unavailable_times_count,
                    'created_date': row[6]
                }

            # 填充表格
            self.constraints_table.setRowCount(len(all_teachers))

            for row, teacher_name in enumerate(all_teachers):
                # 教师姓名
                self.constraints_table.setItem(row, 0, QTableWidgetItem(teacher_name))

                if teacher_name in constraints_dict:
                    # 已设置约束的教师
                    data = constraints_dict[teacher_name]
                    self.constraints_table.setItem(row, 1, QTableWidgetItem(f"{data['max_exams_per_day']}场"))
                    self.constraints_table.setItem(row, 2, QTableWidgetItem("是" if data['no_evening_exams'] else "否"))
                    self.constraints_table.setItem(row, 3, QTableWidgetItem("是" if data['no_weekend_exams'] else "否"))
                    self.constraints_table.setItem(row, 4, QTableWidgetItem(str(data['unavailable_dates_count'])))
                    self.constraints_table.setItem(row, 5, QTableWidgetItem(str(data['unavailable_times_count'])))
                    self.constraints_table.setItem(row, 6, QTableWidgetItem(data['created_date'] or "未知"))

                    # 为已设置约束的行设置背景色（浅绿色）
                    for col in range(7):
                        item = self.constraints_table.item(row, col)
                        if item:
                            item.setBackground(QColor(144, 238, 144))  # 浅绿色
                else:
                    # 未设置约束的教师（使用默认值）
                    self.constraints_table.setItem(row, 1, QTableWidgetItem("3场 (默认)"))
                    self.constraints_table.setItem(row, 2, QTableWidgetItem("否 (默认)"))
                    self.constraints_table.setItem(row, 3, QTableWidgetItem("否 (默认)"))
                    self.constraints_table.setItem(row, 4, QTableWidgetItem("0"))
                    self.constraints_table.setItem(row, 5, QTableWidgetItem("0"))
                    self.constraints_table.setItem(row, 6, QTableWidgetItem("未设置"))

                    # 为未设置约束的行设置背景色（浅黄色）
                    for col in range(7):
                        item = self.constraints_table.item(row, col)
                        if item:
                            item.setBackground(QColor(255, 255, 224))  # 浅黄色

            # 更新状态信息
            total_teachers = len(all_teachers)
            configured_teachers = len(constraints_dict)
            self.setWindowTitle(f'教师约束管理 - 共{total_teachers}位教师，已配置{configured_teachers}位')

            db_manager.close()

        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载教师约束数据失败：{str(e)}')

    def batch_set_constraints(self):
        """批量设置约束"""
        reply = QMessageBox.question(
            self, '确认批量设置',
            f'确定要为所有教师设置以下约束吗？\n\n'
            f'每日最多考试场次：{self.batch_max_exams.value()}场\n'
            f'不在晚上考试：{"是" if self.batch_no_evening.isChecked() else "否"}\n'
            f'不在周末考试：{"是" if self.batch_no_weekend.isChecked() else "否"}\n\n'
            f'注意：这将覆盖所有现有的约束设置！',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                db_manager = DatabaseManager()

                # 获取所有教师
                db_manager.cursor.execute('SELECT DISTINCT 教师 FROM courses WHERE 教师 IS NOT NULL')
                teachers = [row[0] for row in db_manager.cursor.fetchall()]

                success_count = 0
                for teacher in teachers:
                    success = db_manager.set_teacher_constraints(
                        teacher_name=teacher,
                        max_exams_per_day=self.batch_max_exams.value(),
                        no_evening_exams=self.batch_no_evening.isChecked(),
                        no_weekend_exams=self.batch_no_weekend.isChecked(),
                        unavailable_dates=[],
                        unavailable_times=[]
                    )
                    if success:
                        success_count += 1

                db_manager.close()

                QMessageBox.information(
                    self, '批量设置完成',
                    f'成功为 {success_count}/{len(teachers)} 位教师设置了约束'
                )

                # 刷新表格
                self.load_teacher_constraints()

            except Exception as e:
                QMessageBox.warning(self, '错误', f'批量设置约束失败：{str(e)}')

    def init_default_constraints(self):
        """初始化默认约束（只为未设置约束的教师设置）"""
        reply = QMessageBox.question(
            self, '确认初始化',
            '确定要为未设置约束的教师初始化默认约束吗？\n\n'
            '默认约束：\n'
            '- 每日最多3场考试\n'
            '- 不在晚上考试：是\n'
            '- 不在周末考试：是\n'
            '- 无特殊不可用时间\n\n'
            '注意：已设置约束的教师不会被修改',
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                db_manager = DatabaseManager()

                # 获取所有教师
                db_manager.cursor.execute('SELECT DISTINCT 教师 FROM courses WHERE 教师 IS NOT NULL')
                all_teachers = [row[0] for row in db_manager.cursor.fetchall()]

                # 获取已设置约束的教师
                db_manager.cursor.execute('SELECT teacher_name FROM teacher_constraints')
                configured_teachers = set(row[0] for row in db_manager.cursor.fetchall())

                # 为未设置约束的教师设置默认值
                unconfigured_teachers = [t for t in all_teachers if t not in configured_teachers]

                success_count = 0
                for teacher in unconfigured_teachers:
                    success = db_manager.set_teacher_constraints(
                        teacher_name=teacher,
                        max_exams_per_day=3,
                        no_evening_exams=True,  # 默认不在晚上考试
                        no_weekend_exams=True,  # 默认不在周末考试
                        unavailable_dates=[],
                        unavailable_times=[]
                    )
                    if success:
                        success_count += 1

                db_manager.close()

                QMessageBox.information(
                    self, '初始化完成',
                    f'成功为 {success_count}/{len(unconfigured_teachers)} 位未配置的教师设置了默认约束'
                )

                # 刷新表格
                self.load_teacher_constraints()

            except Exception as e:
                QMessageBox.warning(self, '错误', f'初始化默认约束失败：{str(e)}')

    def edit_selected_teacher(self):
        """编辑选中的教师约束"""
        current_row = self.constraints_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, '提示', '请先选择要编辑的教师')
            return

        teacher_name = self.constraints_table.item(current_row, 0).text()

        # 打开约束设置对话框
        dialog = TeacherConstraintsDialog(self, teacher_name)
        if dialog.exec_() == dialog.Accepted:
            # 刷新表格
            self.load_teacher_constraints()

    def delete_selected_constraints(self):
        """删除选中教师的约束设置"""
        current_row = self.constraints_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, '提示', '请先选择要删除约束的教师')
            return

        teacher_name = self.constraints_table.item(current_row, 0).text()

        reply = QMessageBox.question(
            self, '确认删除',
            f'确定要删除教师 {teacher_name} 的约束设置吗？\n\n'
            f'删除后该教师将使用系统默认约束。',
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                db_manager = DatabaseManager()
                db_manager.cursor.execute(
                    'DELETE FROM teacher_constraints WHERE teacher_name = ?',
                    (teacher_name,)
                )
                db_manager.conn.commit()
                db_manager.close()

                QMessageBox.information(self, '删除成功', f'已删除教师 {teacher_name} 的约束设置')

                # 刷新表格
                self.load_teacher_constraints()

            except Exception as e:
                QMessageBox.warning(self, '错误', f'删除约束设置失败：{str(e)}')

    def get_statistics(self):
        """获取约束设置统计信息"""
        try:
            db_manager = DatabaseManager()

            # 总教师数
            db_manager.cursor.execute('SELECT COUNT(DISTINCT 教师) FROM courses WHERE 教师 IS NOT NULL')
            total_teachers = db_manager.cursor.fetchone()[0]

            # 已设置约束的教师数
            db_manager.cursor.execute('SELECT COUNT(*) FROM teacher_constraints')
            configured_teachers = db_manager.cursor.fetchone()[0]

            # 不在晚上考试的教师数
            db_manager.cursor.execute('SELECT COUNT(*) FROM teacher_constraints WHERE no_evening_exams = 1')
            no_evening_count = db_manager.cursor.fetchone()[0]

            # 不在周末考试的教师数
            db_manager.cursor.execute('SELECT COUNT(*) FROM teacher_constraints WHERE no_weekend_exams = 1')
            no_weekend_count = db_manager.cursor.fetchone()[0]

            db_manager.close()

            return {
                'total_teachers': total_teachers,
                'configured_teachers': configured_teachers,
                'no_evening_count': no_evening_count,
                'no_weekend_count': no_weekend_count
            }

        except Exception as e:
            print(f"获取统计信息失败: {e}")
            return None