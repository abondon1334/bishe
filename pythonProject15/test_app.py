import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel

class SimpleWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('测试应用')
        self.setGeometry(100, 100, 400, 200)
        
        layout = QVBoxLayout()
        
        label = QLabel('考试编排系统测试应用')
        layout.addWidget(label)
        
        button = QPushButton('点击测试')
        button.clicked.connect(self.on_click)
        layout.addWidget(button)
        
        self.setLayout(layout)
        
    def on_click(self):
        print('按钮被点击')
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SimpleWindow()
    window.show()
    sys.exit(app.exec_())
