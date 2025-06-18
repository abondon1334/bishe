import sys
import os
import sqlite3
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt5.QtCore import QCoreApplication
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from models.database import DatabaseManager

def is_first_run():
    """
    检查是否是第一次运行程序
    """
    return not os.path.exists('exam_system.db')

def main():
    app = QApplication(sys.argv)
    print("启动应用...")
    
    # 只在第一次运行时删除数据库
    if is_first_run():
        print("首次运行，初始化数据库")
    elif os.path.exists('exam_system.db'):
        # 检查数据库文件是否可用
        try:
            conn = sqlite3.connect('exam_system.db')
            conn.cursor().execute('SELECT name FROM sqlite_master')
            conn.close()
        except sqlite3.Error:
            print("数据库文件损坏，重新创建")
            os.remove('exam_system.db')
    
    # 确保数据库表已正确创建
    db_manager = DatabaseManager()
    print("数据库初始化完成")
    
    login_window = LoginWindow()
    print("显示登录窗口")
    if login_window.exec_() == QDialog.Accepted:
        print("登录成功，获取用户信息")
        # 获取登录用户信息
        username = login_window.username_input.text()
        password = login_window.password_input.text()
        user = db_manager.validate_user(username, password)
        
        if user:
            print(f"成功获取到用户: {user}")
            # 查看用户结构
            print(f"用户数据结构: {[i for i in range(len(user))]}")
            for i, value in enumerate(user):
                print(f"用户字段[{i}]: {value}")
            
            # 默认使用索引3作为角色，索引4作为名称
            role_index = 3 if len(user) > 3 else 2
            name_index = 4 if len(user) > 4 else 1
            
            user_role = user[role_index] if role_index < len(user) else 'teacher'
            user_name = user[name_index] if name_index < len(user) else username
            
            print(f"用户名: {user_name}, 角色: {user_role}")
            
            # 通过用户的角色字段直接创建窗口
            main_window = MainWindow(user_name, user_role)
            
            # 重写关闭事件，添加保存逻辑
            original_close_event = main_window.closeEvent
            def custom_close_event(event):
                # 询问是否保存考试安排
                reply = QMessageBox.question(
                    main_window, 
                    '保存考试安排', 
                    '是否要导出当前的考试安排？', 
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
                )
                
                if reply == QMessageBox.Yes:
                    # 导出考试安排
                    db_manager.export_current_exam_arrangements()
                    event.accept()
                elif reply == QMessageBox.No:
                    event.accept()
                else:
                    event.ignore()
                
                # 调用原始的关闭事件处理
                original_close_event(event)
            
            main_window.closeEvent = custom_close_event
            main_window.show()
            print("主窗口已显示")
        else:
            print("获取用户信息失败")
    else:
        print("登录被取消")
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 