from PyQt5.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QAction
from .exam_arrangement_window import ExamArrangementWindow
from models.database import DatabaseManager
from ui.simple_teacher_view import SimpleTeacherView
from ui.admin_exam_adjustment_review import ExamAdjustmentReviewWindow
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
            
            # 为管理员添加考场调整审核入口
            if self.role == 'admin':
                exam_adjustment_review_tab = ExamAdjustmentReviewWindow()
                tab_widget.addTab(exam_adjustment_review_tab, '考场调整审核')
        
        self.setCentralWidget(tab_widget)

        if self.role == 'teacher':
            self.open_teacher_exam_view()

        # 添加导出考试安排的菜单项
        export_action = QAction('导出考试安排', self)
        export_action.triggered.connect(self.export_exam_arrangements)
        file_menu = self.menuBar().addMenu('文件')
        file_menu.addAction(export_action)

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