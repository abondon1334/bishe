import sys
import pandas as pd
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox,
                             QDialog, QFormLayout, QLineEdit, QComboBox, QLabel,
                             QTabWidget, QSplitter, QDateEdit, QGroupBox, QRadioButton)
from PyQt5.QtCore import Qt, QDate
from utils.excel_importer import ExcelImporter
from utils.exam_scheduler import ExamScheduler
from utils.conflict_detector import ConflictDetector
from models.database import DatabaseManager


class AdjustExamDialog(QDialog):
    def __init__(self, parent=None, arrangement=None):
        super().__init__(parent)
        self.arrangement = arrangement
        self.conflict_detector = ConflictDetector()
        self.setWindowTitle('调整考试安排')

        # 获取当前考试安排的教师和班级信息，用于冲突检测
        self.current_teacher = None
        self.current_class = None
        if arrangement:
            self._get_arrangement_details()

        self.init_ui()

    def _get_arrangement_details(self):
        """获取考试安排的详细信息，包括教师和班级"""
        try:
            db_manager = DatabaseManager()
            query = '''
                SELECT c.教师, c.学院班级
                FROM exam_arrangements ea
                JOIN courses c ON ea.教室号 = c.id
                WHERE ea.arrangement_id = ?
            '''
            db_manager.cursor.execute(query, (self.arrangement['arrangement_id'],))
            result = db_manager.cursor.fetchone()
            if result:
                self.current_teacher = result[0]
                self.current_class = result[1]
            db_manager.close()
        except Exception as e:
            print(f"获取考试安排详细信息失败: {e}")
            # 从arrangement数据中获取备用信息
            self.current_teacher = self.arrangement.get('teacher', '')
            self.current_class = self.arrangement.get('class_name', '')

    def init_ui(self):
        layout = QFormLayout()

        # 显示当前考试安排信息
        if self.arrangement:
            info_text = (
                f"课程：{self.arrangement['course_name']}\n"
                f"班级：{self.arrangement['class_name']}\n"
                f"当前日期：{self.arrangement['current_date']}\n"
                f"当前时间：{self.arrangement['current_time']}\n"
                f"当前教室编号：{self.arrangement.get('current_room_id', '')}\n"
                f"当前教室：{self.arrangement['current_room']}"
            )
            info_label = QLabel(info_text)
            layout.addRow('当前安排:', info_label)

        # 实验室选择
        self.lab_combo = QComboBox()
        self.load_labs()
        layout.addRow('选择新教室:', self.lab_combo)

        # 日期输入
        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText('YYYY-MM-DD')
        self.date_input.setText(self.arrangement['current_date'] if self.arrangement else '')
        layout.addRow('考试日期:', self.date_input)

        # 时间输入
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText('HH:MM-HH:MM')
        self.time_input.setText(self.arrangement['current_time'] if self.arrangement else '')
        layout.addRow('考试时间:', self.time_input)

        # 确定和取消按钮
        buttons = QHBoxLayout()
        confirm_btn = QPushButton('确定')
        cancel_btn = QPushButton('取消')
        confirm_btn.clicked.connect(self.check_and_accept)
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(confirm_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow(buttons)

        self.setLayout(layout)

    def load_labs(self):
        # 从数据库加载实验室列表
        db_manager = DatabaseManager()
        db_manager.cursor.execute('SELECT 教室编号, 教室名称 FROM exam_rooms')
        rooms = db_manager.cursor.fetchall()
        for room_id, room_name in rooms:
            self.lab_combo.addItem(f"{room_id} - {room_name}")

        # 如果有当前教室，设置为默认选中
        if self.arrangement:
            for i in range(self.lab_combo.count()):
                if self.arrangement['current_room'] in self.lab_combo.itemText(i):
                    self.lab_combo.setCurrentIndex(i)
                    break

        db_manager.close()

    def get_selected_data(self):
        # 分割教室编号和名称
        selected_text = self.lab_combo.currentText()
        lab_id = selected_text.split(' - ')[0]
        return {
            'lab_id': lab_id,
            'date': self.date_input.text(),
            'time': self.time_input.text()
        }

    def check_and_accept(self):
        """检查冲突并确认调整"""
        try:
            # 获取用户输入的数据
            selected_text = self.lab_combo.currentText()
            new_room_id = selected_text.split(' - ')[0]
            new_date = self.date_input.text().strip()
            new_time = self.time_input.text().strip()

            # 验证输入
            if not new_date or not new_time:
                QMessageBox.warning(self, '输入错误', '请填写完整的日期和时间')
                return

            # 检查日期格式
            try:
                from datetime import datetime
                datetime.strptime(new_date, '%Y-%m-%d')
            except ValueError:
                QMessageBox.warning(self, '日期格式错误', '请使用正确的日期格式：YYYY-MM-DD')
                return

            # 检查时间格式
            if '-' not in new_time or len(new_time.split('-')) != 2:
                QMessageBox.warning(self, '时间格式错误', '请使用正确的时间格式：HH:MM-HH:MM')
                return

            # 进行冲突检测
            has_conflict, conflicts = self.conflict_detector.check_all_conflicts(
                new_room_id,
                self.current_teacher,
                self.current_class,
                new_date,
                new_time,
                exclude_arrangement_id=self.arrangement['arrangement_id']
            )

            if has_conflict:
                # 格式化冲突信息
                conflict_message = self.conflict_detector.format_conflict_message(conflicts)

                # 显示冲突警告并询问用户是否继续
                reply = QMessageBox.question(
                    self, '检测到冲突',
                    f"检测到以下冲突：\n\n{conflict_message}\n\n是否仍要继续调整？\n\n"
                    f"注意：强制调整可能导致考试时间冲突！",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No  # 默认选择"否"
                )

                if reply == QMessageBox.No:
                    return  # 用户选择不继续

                # 用户选择继续，显示最终确认
                final_reply = QMessageBox.question(
                    self, '最终确认',
                    f"您确定要强制调整到：\n"
                    f"教室：{selected_text}\n"
                    f"日期：{new_date}\n"
                    f"时间：{new_time}\n\n"
                    f"这将忽略冲突警告！",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )

                if final_reply == QMessageBox.No:
                    return
            else:
                # 没有冲突，显示确认信息
                reply = QMessageBox.question(
                    self, '确认调整',
                    f"确认调整到：\n"
                    f"教室：{selected_text}\n"
                    f"日期：{new_date}\n"
                    f"时间：{new_time}\n\n"
                    f"未检测到冲突，可以安全调整。",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )

                if reply == QMessageBox.No:
                    return

            # 用户确认调整，关闭对话框
            self.accept()

        except Exception as e:
            QMessageBox.warning(self, '错误', f'冲突检测失败：{str(e)}')
            print(f"冲突检测错误详情: {e}")
            import traceback
            traceback.print_exc()


class ExamSettingsDialog(QDialog):
    """考试设置对话框，用于设置考试日期范围和每天场次"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('考试设置')
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        # 开始日期
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(7))  # 默认下周
        layout.addRow('开始日期:', self.start_date)

        # 结束日期
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addDays(13))  # 默认下周+6天
        layout.addRow('结束日期:', self.end_date)

        # 每天场次选择
        slots_group = QGroupBox("每天考试场次")
        slots_layout = QVBoxLayout()

        self.four_slots = QRadioButton("四场 (08:00-10:00, 10:30-12:30, 14:00-16:00, 16:30-18:30)")
        self.five_slots = QRadioButton("五场 (增加 19:00-21:00)")
        self.four_slots.setChecked(True)  # 默认选择四场

        slots_layout.addWidget(self.four_slots)
        slots_layout.addWidget(self.five_slots)
        slots_group.setLayout(slots_layout)

        layout.addRow(slots_group)

        # 确定和取消按钮
        buttons = QHBoxLayout()
        confirm_btn = QPushButton('确定')
        cancel_btn = QPushButton('取消')
        confirm_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(confirm_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow(buttons)

        self.setLayout(layout)

    def get_settings(self):
        """获取用户设置的值"""
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        slots_per_day = 5 if self.five_slots.isChecked() else 4

        return {
            'start_date': start_date,
            'end_date': end_date,
            'slots_per_day': slots_per_day
        }


class ExamArrangementWindow(QWidget):
    def __init__(self, role):
        super().__init__()
        self.role = role
        self.db_manager = DatabaseManager()
        self.excel_importer = ExcelImporter()
        self.exam_scheduler = ExamScheduler()
        # 默认排课设置
        self.exam_settings = {
            'start_date': None,  # 使用默认值（下周一）
            'end_date': None,  # 使用默认值（开始日期+6天）
            'slots_per_day': 4  # 默认每天4场考试
        }
        self.init_ui()

    def init_ui(self):
        # 主布局为水平布局
        main_layout = QHBoxLayout(self)

        # 创建左侧面板
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)

        # 创建选项卡
        left_tab = QTabWidget()

        # 按钮面板
        button_panel = QWidget()
        button_layout = QVBoxLayout(button_panel)
        button_layout.setSpacing(10)

        # 按钮列表
        button_configs = [
            ('导入课程表', self.import_course_table),
            ('导入实验室配置', self.import_lab_config),
            ('自动排考场', self.schedule_exams),
            ('导出考场', self.export_exam_arrangements),
            ('调整考场', self.adjust_exam_arrangement)
        ]

        # 创建并添加按钮
        for text, connect_func in button_configs:
            btn = QPushButton(text)
            btn.setMinimumHeight(40)  # 调整按钮高度
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    background-color: #f0f0f0;
                    border: 2px solid #a0a0a0;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
            btn.clicked.connect(connect_func)
            button_layout.addWidget(btn)

        # 根据角色控制按钮可用性
        if self.role == 'teacher':
            for i in range(button_layout.count()):
                widget = button_layout.itemAt(i).widget()
                if isinstance(widget, QPushButton):
                    if widget.text() in ['导入课程表', '导入实验室配置', '自动排考场', '调整考场']:
                        widget.setEnabled(False)

        if self.role == 'scheduler':
            # 排课员可以排课和调整，但不能导入课程
            for i in range(button_layout.count()):
                widget = button_layout.itemAt(i).widget()
                if isinstance(widget, QPushButton):
                    if widget.text() == '导入课程表':
                        widget.setEnabled(False)

        # 添加一些弹性空间
        button_layout.addStretch()

        # 创建表格面板
        tables_widget = QWidget()
        tables_layout = QVBoxLayout(tables_widget)

        # 创建两个表格用于显示导入的数据
        self.courses_table = QTableWidget()
        self.courses_table.setColumnCount(5)
        self.courses_table.setHorizontalHeaderLabels(['课程名称', '教师', '教室号', '时段', '考试人数'])

        self.rooms_table = QTableWidget()
        self.rooms_table.setColumnCount(4)
        self.rooms_table.setHorizontalHeaderLabels(['教室编号', '教室名称', '教室容量', '教学楼'])

        # 创建选项卡并添加表格
        tabs = QTabWidget()
        tabs.addTab(self.courses_table, "课程表")
        tabs.addTab(self.rooms_table, "教室表")

        tables_layout.addWidget(tabs)

        # 添加按钮面板和表格面板到左侧选项卡
        left_tab.addTab(button_panel, "操作")
        left_tab.addTab(tables_widget, "导入数据")

        left_layout.addWidget(left_tab)

        # 右侧表格区域
        right_panel = QVBoxLayout()

        # 考场安排表格
        self.exam_table = QTableWidget()
        self.exam_table.setColumnCount(7)
        self.exam_table.setHorizontalHeaderLabels(
            ['课程名称', '学院班级', '教师', '考试日期', '考试时间', '教室编号', '教室名称', ])

        right_panel.addWidget(self.exam_table)

        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)

        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        splitter.addWidget(right_widget)

        # 设置初始分割比例
        splitter.setSizes([300, 700])

        # 将分割器添加到主布局
        main_layout.addWidget(splitter)

        # 设置主布局
        self.setLayout(main_layout)

    def import_course_table(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '选择课程表', '', 'Excel Files (*.xlsx *.xls)')
        if file_path:
            try:
                # 导入课程表
                df = pd.read_excel(file_path)
                self.excel_importer.import_courses(file_path)

                # 在左侧表格中显示导入的数据
                self.display_courses_table(df)

                QMessageBox.information(self, '提示', '课程表导入成功')
            except Exception as e:
                QMessageBox.warning(self, '错误', f'导入失败：{str(e)}')

    def import_lab_config(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '选择实验室配置', '', 'Excel Files (*.xlsx *.xls)')
        if file_path:
            try:
                # 导入教室配置
                df = pd.read_excel(file_path)
                self.excel_importer.import_labs(file_path)

                # 在左侧表格中显示导入的数据
                self.display_rooms_table(df)

                QMessageBox.information(self, '提示', '实验室配置导入成功')
            except Exception as e:
                QMessageBox.warning(self, '错误', f'导入失败：{str(e)}')

    def display_courses_table(self, df):
        """显示导入的课程表数据"""
        # 清空表格
        self.courses_table.setRowCount(0)

        # 设置行数
        self.courses_table.setRowCount(len(df))

        # 填充数据
        for row_idx, row in df.iterrows():
            self.courses_table.setItem(row_idx, 0, QTableWidgetItem(str(row.get('课程名称', ''))))
            self.courses_table.setItem(row_idx, 1, QTableWidgetItem(str(row.get('教师', ''))))
            self.courses_table.setItem(row_idx, 2, QTableWidgetItem(str(row.get('教室号', ''))))
            self.courses_table.setItem(row_idx, 3, QTableWidgetItem(str(row.get('时段', ''))))
            self.courses_table.setItem(row_idx, 4, QTableWidgetItem(str(row.get('考试人数', ''))))

    def display_rooms_table(self, df):
        """显示导入的教室表数据"""
        # 清空表格
        self.rooms_table.setRowCount(0)

        # 设置行数
        self.rooms_table.setRowCount(len(df))

        # 填充数据
        for row_idx, row in df.iterrows():
            self.rooms_table.setItem(row_idx, 0, QTableWidgetItem(str(row.get('教室编号', ''))))
            self.rooms_table.setItem(row_idx, 1, QTableWidgetItem(str(row.get('教室名称', ''))))
            self.rooms_table.setItem(row_idx, 2, QTableWidgetItem(str(row.get('教室容量', ''))))
            self.rooms_table.setItem(row_idx, 3, QTableWidgetItem(str(row.get('教学楼', ''))))

    def schedule_exams(self):
        try:
            # 打开设置对话框
            settings_dialog = ExamSettingsDialog(self)
            if settings_dialog.exec_() == QDialog.Accepted:
                # 获取用户设置
                self.exam_settings = settings_dialog.get_settings()

                # 调用新的排课算法，传入设置参数
                success, message, failed_courses = self.exam_scheduler.schedule_exams(
                    start_date=self.exam_settings['start_date'],
                    end_date=self.exam_settings['end_date'],
                    slots_per_day=self.exam_settings['slots_per_day']
                )

                if success:
                    QMessageBox.information(self, '排考成功', message)
                    # 刷新考试安排预览
                    self.preview_exam_arrangements()
                else:
                    # 显示详细的失败信息
                    reply = QMessageBox.question(
                        self, '排考未完全成功',
                        f"{message}\n\n是否查看已成功安排的考试？",
                        QMessageBox.Yes | QMessageBox.No
                    )

                    if reply == QMessageBox.Yes:
                        # 刷新考试安排预览，显示部分成功的结果
                        self.preview_exam_arrangements()

                        # 如果有失败的课程，提供建议
                        if failed_courses:
                            self.show_scheduling_suggestions(failed_courses)
        except Exception as e:
            QMessageBox.warning(self, '错误', f'排课失败：{str(e)}')

    def show_scheduling_suggestions(self, failed_courses):
        """
        显示排考建议对话框
        """
        suggestion_text = "以下课程未能安排考试，建议：\n\n"

        for course in failed_courses[:5]:  # 只显示前5个
            suggestion_text += f"• {course['course_name']} ({course['teacher']})\n"
            suggestion_text += f"  班级: {course['class_name']}, 人数: {course['students_count']}\n"
            suggestion_text += f"  原因: {course['reason']}\n\n"

        if len(failed_courses) > 5:
            suggestion_text += f"... 还有 {len(failed_courses) - 5} 门课程\n\n"

        suggestion_text += "建议解决方案:\n"
        suggestion_text += "1. 手动调整教师时间约束\n"
        suggestion_text += "2. 延长考试周期\n"
        suggestion_text += "3. 增加考试场次\n"
        suggestion_text += "4. 手动安排这些课程"

        QMessageBox.information(self, '排考建议', suggestion_text)

    def preview_exam_arrangements(self):
        """
        预览考试安排，包含教学楼信息
        """
        try:
            # 使用新的查询方法获取包含教学楼的考试安排
            arrangements = self.db_manager.get_exam_arrangements_with_building()

            if not arrangements:
                QMessageBox.information(self, '提示', '暂无考试安排数据')
                return

            # 打印查询结果
            print("考试安排数量:", len(arrangements))
            if arrangements:
                print("第一行考试安排:", arrangements[0])

            # 设置表格列数和标题，添加教室编号和教学楼列
            self.exam_table.setColumnCount(9)
            self.exam_table.setHorizontalHeaderLabels([
                '课程名称', '学院班级', '教师', '考试日期',
                '考试时间', '教室编号', '教室名称', '教学楼', '考试人数',
            ])

            # 填充数据
            self.exam_table.setRowCount(len(arrangements))
            for row, arrangement in enumerate(arrangements):
                for col in range(9):
                    self.exam_table.setItem(row, col, QTableWidgetItem(str(arrangement[col])))

            # 调整列宽
            self.exam_table.resizeColumnsToContents()

            # 显示统计信息
            total_exams = len(arrangements)
            unique_dates = len(set(arr[3] for arr in arrangements))
            unique_teachers = len(set(arr[2] for arr in arrangements))
            unique_buildings = len(set(arr[7] for arr in arrangements if arr[7]))

            stats_text = f"考试安排统计: 共 {total_exams} 场考试, {unique_dates} 个考试日期, {unique_teachers} 位教师, {unique_buildings} 个教学楼"
            print(stats_text)

        except Exception as e:
            print(f"预览考试安排出错: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, '错误', f'预览考试安排失败：{str(e)}')

    def export_exam_arrangements(self):
        file_path, _ = QFileDialog.getSaveFileName(self, '导出考场安排', '', 'Excel Files (*.xlsx)')
        if file_path:
            try:
                # 从数据库读取考试安排
                df = pd.read_sql_query('''
                    SELECT 
                        c.课程名称, 
                        c.学院班级, 
                        c.教师, 
                        ea.考试日期, 
                        ea.考试时间, 
                        er.教室编号,
                        er.教室名称,
                        er.教学楼
                    FROM exam_arrangements ea
                    JOIN courses c ON ea.教室号 = c.id
                    JOIN exam_rooms er ON ea.教室编号 = er.教室编号
                ''', self.db_manager.conn)


                # 导出到Excel
                df.to_excel(file_path, index=False)
                QMessageBox.information(self, '提示', '考场安排导出成功')
            except Exception as e:
                QMessageBox.warning(self, '错误', f'导出失败：{str(e)}')

    def adjust_exam_arrangement(self):
        # 获取当前选中的行
        current_row = self.exam_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, '提示', '请先选择要调整的考试安排')
            return

        try:
            # 获取选中行的考试信息
            course_name = self.exam_table.item(current_row, 0).text()
            class_name = self.exam_table.item(current_row, 1).text()
            exam_date = self.exam_table.item(current_row, 3).text()
            exam_time = self.exam_table.item(current_row, 4).text()
            room_id = self.exam_table.item(current_row, 5).text()
            room_name = self.exam_table.item(current_row, 6).text()

            # 查询对应的安排ID
            query = """
                SELECT ea.arrangement_id
                FROM exam_arrangements ea
                JOIN courses c ON ea.教室号 = c.id
                WHERE c.课程名称 = ? AND c.学院班级 = ? 
                AND ea.考试日期 = ? AND ea.考试时间 = ?
            """
            self.db_manager.cursor.execute(query, (course_name, class_name, exam_date, exam_time))
            result = self.db_manager.cursor.fetchone()

            if not result:
                QMessageBox.warning(self, '错误', '无法获取选中考试的安排ID')
                return

            arrangement_id = result[0]

            # 准备考试安排数据
            arrangement_data = {
                'arrangement_id': arrangement_id,
                'course_name': course_name,
                'class_name': class_name,
                'current_date': exam_date,
                'current_time': exam_time,
                'current_room_id': room_id,
                'current_room': room_name
            }

            # 打开调整对话框
            dialog = AdjustExamDialog(self, arrangement_data)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_selected_data()

                # 调用调整方法
                success = self.exam_scheduler.adjust_exam_arrangement(
                    arrangement_id,
                    data['lab_id'],
                    data['date'],
                    data['time']
                )

                if success:
                    QMessageBox.information(self, '提示', '考试安排调整成功')
                    # 重新加载考试安排
                    self.preview_exam_arrangements()
                else:
                    QMessageBox.warning(self, '错误', '考试安排调整失败')

        except Exception as e:
            # 统一处理所有异常
            QMessageBox.warning(self, '错误', f'操作失败：{str(e)}')
            import traceback
            traceback.print_exc()  # 打印详细错误堆栈


class TeacherConstraintsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        # 教师姓名输入
        self.teacher_name_input = QLineEdit()
        layout.addRow("教师姓名:", self.teacher_name_input)

        # 允许晚间考试复选框
        self.allow_evening_checkbox = QCheckBox("允许晚间考试")
        layout.addRow("晚间考试:", self.allow_evening_checkbox)

        # 保存按钮
        save_btn = QPushButton("保存约束")
        save_btn.clicked.connect(self.save_constraints)
        layout.addRow(save_btn)

        self.setLayout(layout)

    def save_constraints(self):
        teacher_name = self.teacher_name_input.text()
        allow_evening = 1 if self.allow_evening_checkbox.isChecked() else 0

        # 插入或更新教师约束
        self.db_manager.cursor.execute('''
        INSERT OR REPLACE INTO teacher_constraints (teacher_name, allow_evening_exam)
        VALUES (?, ?)
        ''', (teacher_name, allow_evening))
        self.db_manager.conn.commit()
        QMessageBox.information(self, "成功", "教师约束已保存")