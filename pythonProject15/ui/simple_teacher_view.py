import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLabel, QMessageBox, 
                             QApplication)
from PyQt5.QtCore import Qt
from models.database import DatabaseManager

class SimpleTeacherView(QWidget):
    def __init__(self, teacher_name):
        super().__init__()
        self.teacher_name = teacher_name
        self.db_manager = DatabaseManager()
        self.setWindowTitle(f'考试安排查看 - {self.teacher_name}')
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # 标题标签
        title_label = QLabel(f'欢迎 {self.teacher_name} 老师')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet('font-size: 18px; font-weight: bold;')
        main_layout.addWidget(title_label)
        
        # 功能按钮
        button_layout = QHBoxLayout()
        refresh_button = QPushButton('刷新')
        refresh_button.clicked.connect(self.refresh_exam_arrangements)
        button_layout.addWidget(refresh_button)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # 表格
        self.exam_table = QTableWidget()
        self.exam_table.setColumnCount(5)
        self.exam_table.setHorizontalHeaderLabels(['课程名称', '考试日期', '考试时间', '教室名称', '考试人数'])
        main_layout.addWidget(self.exam_table)
        
        self.setLayout(main_layout)
        
        # 加载数据
        self.refresh_exam_arrangements()
        
    def refresh_exam_arrangements(self):
        try:
            # 查询考试安排
            query = '''
                SELECT 
                    c.课程名称, 
                    ea.考试日期, 
                    ea.考试时间, 
                    er.教室名称,
                    ea.考试人数
                FROM exam_arrangements ea
                JOIN courses c ON ea.教室号 = c.id
                JOIN exam_rooms er ON ea.教室编号 = er.教室编号
                WHERE c.教师 = ?
            '''
            
            self.db_manager.cursor.execute(query, (self.teacher_name,))
            arrangements = self.db_manager.cursor.fetchall()

            # 清空表格
            self.exam_table.setRowCount(0)

            # 填充表格
            for row_data in arrangements:
                row_position = self.exam_table.rowCount()
                self.exam_table.insertRow(row_position)
                for col, value in enumerate(row_data):
                    self.exam_table.setItem(row_position, col, QTableWidgetItem(str(value)))
            
            # 显示统计信息
            if not arrangements:
                QMessageBox.information(self, '提示', '没有找到您的考试安排')

        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载考试安排失败：{str(e)}')
            import traceback
            traceback.print_exc()


def main():
    app = QApplication(sys.argv)
    view = SimpleTeacherView('张三')  # 测试用
    view.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 