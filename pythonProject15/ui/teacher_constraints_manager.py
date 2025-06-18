from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QMessageBox, QHeaderView,
                             QLabel, QGroupBox, QCheckBox, QSpinBox, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QKeySequence
from models.database import DatabaseManager


# 注意：不再导入外部的teacher_constraints_dialog，避免循环导入

class SimpleTeacherConstraintsEditor(QDialog):
    """简化的教师约束编辑器（内置版本，避免循环导入）"""

    def __init__(self, parent=None, teacher_name=""):
        super().__init__(parent)
        self.teacher_name = teacher_name
        self.setWindowTitle(f'编辑教师约束 - {teacher_name}')
        self.setMinimumSize(400, 500)
        self.setModal(True)
        self.init_ui()
        self.load_current_constraints()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 标题
        title_label = QLabel(f"设置教师约束：{self.teacher_name}")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # 基本约束设置
        basic_group = QGroupBox("基本约束设置")
        basic_layout = QFormLayout()

        # 每日最多考试场次
        self.max_exams_spin = QSpinBox()
        self.max_exams_spin.setRange(1, 10)
        self.max_exams_spin.setValue(3)
        self.max_exams_spin.setSuffix(" 场")
        basic_layout.addRow("每日最多考试场次:", self.max_exams_spin)

        # 晚上考试约束
        self.no_evening_check = QCheckBox("不在晚上考试 (19:00-21:00)")
        self.no_evening_check.setChecked(True)
        basic_layout.addRow(self.no_evening_check)

        # 周末考试约束
        self.no_weekend_check = QCheckBox("不在周末考试")
        self.no_weekend_check.setChecked(True)
        basic_layout.addRow(self.no_weekend_check)

        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)

        # 说明信息
        info_label = QLabel("""
约束说明：
• 每日最多考试场次：限制教师每天的考试监考数量
• 不在晚上考试：避免在19:00-21:00时间段安排考试
• 不在周末考试：避免在周六、周日安排考试
• 更多高级约束请联系系统管理员
        """)
        info_label.setStyleSheet("color: #7f8c8d; background-color: #f8f9fa; padding: 10px; border-radius: 5px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        layout.addStretch()

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_btn = QPushButton("保存约束")
        cancel_btn = QPushButton("取消")

        save_btn.clicked.connect(self.save_constraints)
        cancel_btn.clicked.connect(self.reject)

        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)

        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        # 设置整体样式
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

    def load_current_constraints(self):
        """加载当前教师的约束设置"""
        try:
            db_manager = DatabaseManager()
            constraints = db_manager.get_teacher_constraints(self.teacher_name)

            if constraints:
                self.max_exams_spin.setValue(constraints.get('max_exams_per_day', 3))
                self.no_evening_check.setChecked(constraints.get('no_evening_exams', True))
                self.no_weekend_check.setChecked(constraints.get('no_weekend_exams', True))
            else:
                # 使用默认值（已在UI初始化时设置）
                pass

            db_manager.close()

        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载教师约束时发生错误：{str(e)}')

    def save_constraints(self):
        """保存约束设置"""
        try:
            db_manager = DatabaseManager()

            success = db_manager.set_teacher_constraints(
                teacher_name=self.teacher_name,
                max_exams_per_day=self.max_exams_spin.value(),
                no_evening_exams=self.no_evening_check.isChecked(),
                no_weekend_exams=self.no_weekend_check.isChecked(),
                unavailable_dates=[],  # 简化版本暂不支持
                unavailable_times=[]  # 简化版本暂不支持
            )

            db_manager.close()

            if success:
                QMessageBox.information(self, '保存成功', f'已成功保存教师 {self.teacher_name} 的约束设置')
                self.accept()
            else:
                QMessageBox.warning(self, '保存失败', '保存约束设置时发生错误，请重试')

        except Exception as e:
            QMessageBox.warning(self, '错误', f'保存约束设置时发生错误：{str(e)}')


class TeacherConstraintsManager(QDialog):
    """教师约束管理界面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('教师约束管理')
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)  # 设置默认大小

        # 设置窗口属性
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowMinMaxButtonsHint)
        self.setModal(False)  # 非模态窗口，允许同时操作主窗口

        self.init_ui()
        self.load_teacher_constraints()

        # 设置快捷键
        self.setShortcut()

    def setShortcut(self):
        """设置快捷键"""
        from PyQt5.QtWidgets import QShortcut
        # Ctrl+W 或 Escape 关闭窗口
        close_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        close_shortcut.activated.connect(self.close)

        escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        escape_shortcut.activated.connect(self.close)

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 标题和控制按钮区域
        header_layout = QHBoxLayout()
        title_label = QLabel("教师约束管理")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        # 帮助按钮
        help_btn = QPushButton("使用说明")
        help_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                margin-right: 10px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:pressed {
                background-color: #d35400;
            }
        """)
        help_btn.clicked.connect(self.show_window_info)
        header_layout.addWidget(help_btn)

        # 窗口控制按钮
        close_btn = QPushButton("关闭窗口")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)

        layout.addLayout(header_layout)

        # 操作按钮区域
        action_layout = QHBoxLayout()
        action_layout.addStretch()

        refresh_btn = QPushButton("刷新")
        batch_set_btn = QPushButton("批量设置")
        init_default_btn = QPushButton("初始化默认约束")

        refresh_btn.clicked.connect(self.load_teacher_constraints)
        batch_set_btn.clicked.connect(self.batch_set_constraints)
        init_default_btn.clicked.connect(self.init_default_constraints)

        action_layout.addWidget(refresh_btn)
        action_layout.addWidget(batch_set_btn)
        action_layout.addWidget(init_default_btn)

        layout.addLayout(action_layout)

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

        # 底部控制区域
        bottom_layout = QHBoxLayout()

        # 左侧：统计信息
        stats_label = QLabel("使用 双击 或 选中后点击编辑 来设置教师约束")
        stats_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        bottom_layout.addWidget(stats_label)

        bottom_layout.addStretch()

        # 右侧：操作按钮
        edit_btn = QPushButton("编辑选中教师")
        delete_btn = QPushButton("删除选中约束")
        return_btn = QPushButton("返回主界面")

        edit_btn.clicked.connect(self.edit_selected_teacher)
        delete_btn.clicked.connect(self.delete_selected_constraints)
        return_btn.clicked.connect(self.close)

        return_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)

        bottom_layout.addWidget(edit_btn)
        bottom_layout.addWidget(delete_btn)
        bottom_layout.addWidget(return_btn)

        layout.addLayout(bottom_layout)

        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
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
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                gridline-color: #eee;
            }
            QTableWidget::item {
                border-bottom: 1px solid #eee;
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QLabel {
                color: #2c3e50;
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
        """编辑选中的教师约束（使用内置编辑器，无导入问题）"""
        current_row = self.constraints_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, '提示', '请先选择要编辑的教师')
            return

        teacher_name = self.constraints_table.item(current_row, 0).text()

        try:
            # 使用内置的简化编辑器，完全避免导入问题
            editor = SimpleTeacherConstraintsEditor(self, teacher_name)

            if editor.exec_() == editor.Accepted:
                # 刷新表格显示
                self.load_teacher_constraints()
                QMessageBox.information(
                    self, '编辑成功',
                    f'已成功更新教师 {teacher_name} 的约束设置'
                )

        except Exception as e:
            QMessageBox.warning(
                self, '错误',
                f'打开教师约束编辑器时发生错误：\n\n{str(e)}\n\n'
                f'请检查系统状态或联系技术支持。'
            )

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

    def closeEvent(self, event):
        """重写关闭事件，添加确认对话框"""
        reply = QMessageBox.question(
            self, '确认关闭',
            '确定要关闭教师约束管理窗口吗？\n\n未保存的更改将丢失。',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            event.accept()
            # 通知父窗口管理器窗口已关闭
            if hasattr(self.parent(), 'constraints_manager'):
                self.parent().constraints_manager = None
        else:
            event.ignore()

    def show_window_info(self):
        """显示窗口使用提示"""
        info_text = """
        教师约束管理窗口使用说明：

        • 双击教师行可以编辑约束设置
        • 绿色背景：已设置约束的教师
        • 黄色背景：使用默认约束的教师
        • 可以批量设置所有教师的默认约束
        • 支持快捷键：Ctrl+W 或 Escape 关闭窗口

        功能按钮：
        • 刷新：重新加载数据
        • 批量设置：为所有教师应用相同约束
        • 初始化默认约束：仅为未设置的教师添加约束
        • 编辑选中教师：编辑当前选中的教师约束
        • 删除选中约束：移除教师的自定义约束

        约束编辑功能：
        • 内置简化编辑器，稳定可靠
        • 支持基本约束：每日考试数量、晚上考试、周末考试
        • 自动保存和验证设置
        • 高级约束功能请联系系统管理员
        """
        QMessageBox.information(self, '使用说明', info_text)