from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QWidget, 
                             QHBoxLayout, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt
from models.database import DatabaseManager
from utils.styles import GLOBAL_STYLESHEET, COLORS, add_shadow_effect

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.setWindowTitle('考试编排系统 - 登录')
        self.setFixedWidth(350)  # 增加宽度
        self.setMinimumHeight(400)  # 增加最小高度
        
        # 创建一个登录框容器
        self.login_frame = QWidget(self)
        
        self.setup_ui()

    def setup_ui(self):
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)  # 增加边距
        main_layout.setSpacing(10)

        # 标题
        title_label = QLabel('考试编排系统')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
        """)
        main_layout.addWidget(title_label)
        
        # 登录框布局
        frame_layout = QVBoxLayout(self.login_frame)
        frame_layout.setSpacing(15)
        
        # 用户名
        username_layout = QVBoxLayout()
        username_label = QLabel('用户名:')
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('请输入用户名')
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        
        # 密码
        password_layout = QVBoxLayout()
        password_label = QLabel('密码:')
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('请输入密码')
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        login_button = QPushButton('登录')
        register_button = QPushButton('注册')
        login_button.clicked.connect(self.login)
        register_button.clicked.connect(self.register)
        
        button_layout.addWidget(login_button)
        button_layout.addWidget(register_button)
        
        # 添加到frame_layout
        frame_layout.addLayout(username_layout)
        frame_layout.addLayout(password_layout)
        frame_layout.addLayout(button_layout)
        
        # 添加弹性空间
        frame_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # 将login_frame添加到主布局
        main_layout.addWidget(self.login_frame)
        
        # 设置全局样式
        self.setStyleSheet(GLOBAL_STYLESHEET + f"""
            QLabel {{
                font-size: 14px;
                color: {COLORS['text_dark']};
            }}
            QLineEdit {{
                padding: 10px;
                border: 2px solid {COLORS['primary']};
                border-radius: 15px;
                background-color: white;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['secondary']};
                box-shadow: 0 0 10px rgba(52, 152, 219, 0.5);
            }}
            QPushButton {{
                padding: 10px;
                font-size: 16px;
                min-width: 100px;
            }}
        """)

        # 为登录框添加阴影
        add_shadow_effect(self.login_frame)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        # 修改登录逻辑，不再检查角色
        user = self.db_manager.validate_user(username, password)
        
        if user:
            self.accept()  # 登录成功
        else:
            QMessageBox.warning(self, '登录失败', '用户名或密码错误')

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, '注册失败', '用户名和密码不能为空')
            return

        # 默认注册为教师角色
        success = self.db_manager.add_user(username, password, 'teacher', username)
        
        if success:
            QMessageBox.information(self, '注册成功', '用户注册成功')
        else:
            QMessageBox.warning(self, '注册失败', '用户名已存在') 