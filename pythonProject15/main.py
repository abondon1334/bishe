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
    
    login_window = LoginWindow()
    if login_window.exec_() == QDialog.Accepted:
        # 获取登录用户信息
        user = db_manager.validate_user(
            login_window.username_input.text(), 
            login_window.password_input.text()
        )
        
        if user:
            # 通过用户的角色字段直接创建窗口，无需额外检查
            main_window = MainWindow(user[4], user[3])  # name, role
            
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
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 