from PyQt5.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QAction
from .exam_arrangement_window import ExamArrangementWindow
from models.database import DatabaseManager
from utils.styles import GLOBAL_STYLESHEET, COLORS, add_shadow_effect


class MainWindow(QMainWindow):
    def __init__(self, username, role):
        super().__init__()
        self.username = username
        self.role = role
        self.db_manager = DatabaseManager()
        self.setWindowTitle(f'考试编排系统 - {self.username} ({self.role_name()})')
        self.setup_ui()

    def role_name(self):
        role_names = {
            'admin': '管理员',
            'teacher': '教师',
            'scheduler': '排课员'
        }
        return role_names.get(self.role, '未知角色')

    def setup_ui(self):
        tab_widget = QTabWidget()

        # 根据角色控制功能
        if self.role in ['admin', 'scheduler']:
            exam_arrangement_tab = ExamArrangementWindow(self.role)
            tab_widget.addTab(exam_arrangement_tab, '考试编排')

        self.setCentralWidget(tab_widget)

        if self.role == 'teacher':
            self.open_teacher_exam_view()

        # 创建菜单栏
        self.create_menu_bar()

        self.setStyleSheet(GLOBAL_STYLESHEET + f"""
            QTabWidget::pane {{
                border: 2px solid {COLORS['border']};
                border-radius: 10px;
                background-color: white;
            }}
            QTabBar::tab {{
                background-color: {COLORS['background']};
                color: {COLORS['text_dark']};
                padding: 10px 20px;
                border-radius: 10px;
                margin-right: 5px;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['primary']};
                color: {COLORS['text_light']};
            }}
        """)

        # 为标签页添加阴影
        add_shadow_effect(self.centralWidget())

    def create_menu_bar(self):
        """创建菜单栏"""
        # 文件菜单
        file_menu = self.menuBar().addMenu('文件')

        export_action = QAction('导出考试安排', self)
        export_action.triggered.connect(self.export_exam_arrangements)
        file_menu.addAction(export_action)

        # 管理菜单（仅管理员和排课员可用）
        if self.role in ['admin', 'scheduler']:
            manage_menu = self.menuBar().addMenu('管理')

            # 教师约束管理
            constraints_action = QAction('教师约束管理', self)
            constraints_action.triggered.connect(self.open_teacher_constraints_manager)
            manage_menu.addAction(constraints_action)

            # 分隔线
            manage_menu.addSeparator()

            # 其他管理功能可以在这里添加
            if self.role == 'admin':
                # 管理员专用功能
                user_management_action = QAction('用户管理', self)
                user_management_action.triggered.connect(self.open_user_management)
                user_management_action.setEnabled(False)  # 暂未实现
                manage_menu.addAction(user_management_action)

        # 帮助菜单
        help_menu = self.menuBar().addMenu('帮助')

        about_action = QAction('关于系统', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def open_teacher_constraints_manager(self):
        """打开教师约束管理窗口"""
        try:
            from ui.teacher_constraints_manager import TeacherConstraintsManager
            self.constraints_manager = TeacherConstraintsManager(self)
            self.constraints_manager.show()
        except Exception as e:
            QMessageBox.warning(self, '错误', f'打开教师约束管理失败：{str(e)}')

    def open_user_management(self):
        """打开用户管理窗口（暂未实现）"""
        QMessageBox.information(self, '提示', '用户管理功能暂未实现')

    def show_about(self):
        """显示关于信息"""
        about_text = """
        考试编排系统 v1.0

        主要功能：
        • 课程表和教室配置导入
        • 智能考试安排算法
        • 教师时间约束管理
        • 考试冲突检测和调整
        • 考试安排导出

        开发信息：
        • 基于PyQt5开发
        • 支持多角色权限控制
        • 智能排课和冲突预防
        """
        QMessageBox.about(self, '关于考试编排系统', about_text)

    def open_teacher_exam_view(self):
        self.teacher_exam_view = SimpleTeacherView(self.username)
        self.teacher_exam_view.show()

    def export_exam_arrangements(self):
        """
        手动导出考试安排
        """
        try:
            db_manager = DatabaseManager()
            file_path = db_manager.export_current_exam_arrangements()

            if file_path:
                QMessageBox.information(self, '导出成功', f'考试安排已导出到：{file_path}')
        except Exception as e:
            QMessageBox.warning(self, '导出失败', str(e)) 