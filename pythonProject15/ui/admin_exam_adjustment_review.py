from PyQt5.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem, 
                             QVBoxLayout, QHBoxLayout, QPushButton, 
                             QMessageBox, QLabel)
from PyQt5.QtCore import Qt
from models.database import DatabaseManager

class ExamAdjustmentReviewWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 标题
        title_label = QLabel('考场调整申请审核')
        title_label.setStyleSheet('font-size: 18px; font-weight: bold;')
        layout.addWidget(title_label)

        # 申请列表表格
        self.request_table = QTableWidget()
        self.request_table.setColumnCount(11)
        self.request_table.setHorizontalHeaderLabels([
            '申请ID', '课程名称', '学院班级', '申请人', 
            '原日期', '原时间', '原教室', 
            '新日期', '新时间', '新教室', '申请理由'
        ])
        self.request_table.horizontalHeader().setStretchLastSection(True)

        # 审核按钮区
        button_layout = QHBoxLayout()
        approve_btn = QPushButton('同意申请')
        reject_btn = QPushButton('拒绝申请')
        approve_btn.clicked.connect(self.approve_request)
        reject_btn.clicked.connect(self.reject_request)
        button_layout.addWidget(approve_btn)
        button_layout.addWidget(reject_btn)

        layout.addWidget(self.request_table)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        
        # 加载申请
        self.load_requests()

    def load_requests(self):
        try:
            # 加载待审核的申请
            query = '''
                SELECT 
                    ear.request_id, 
                    c.课程名称, 
                    c.学院班级, 
                    ear.申请人,
                    ear.原考试日期, 
                    ear.原考试时间, 
                    ear.原教室,
                    ear.新考试日期, 
                    ear.新考试时间, 
                    ear.新教室, 
                    ear.申请理由
                FROM exam_adjustment_requests ear
                JOIN exam_arrangements ea ON ear.arrangement_id = ea.arrangement_id
                JOIN courses c ON ea.教室号 = c.id
                WHERE ear.状态 = '待审核'
            '''
            
            self.db_manager.cursor.execute(query)
            requests = self.db_manager.cursor.fetchall()

            # 清空表格
            self.request_table.setRowCount(0)

            # 填充表格
            for row_data in requests:
                row_position = self.request_table.rowCount()
                self.request_table.insertRow(row_position)
                for col, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.request_table.setItem(row_position, col, item)

        except Exception as e:
            QMessageBox.warning(self, '错误', f'加载申请失败：{str(e)}')

    def check_exam_conflict(self, new_date, new_time, new_room):
        """
        检查新的考试安排是否与现有安排冲突
        """
        try:
            query = '''
                SELECT COUNT(*) FROM exam_arrangements 
                WHERE 考试日期 = ? AND 考试时间 = ? AND 教室编号 = ?
            '''
            self.db_manager.cursor.execute(query, (new_date, new_time, new_room))
            conflict_count = self.db_manager.cursor.fetchone()[0]
            return conflict_count > 0
        except Exception as e:
            QMessageBox.warning(self, '错误', f'检查冲突失败：{str(e)}')
            return True

    def approve_request(self):
        # 获取选中的申请
        current_row = self.request_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, '提示', '请选择要审核的申请')
            return

        # 获取申请详情
        request_id = self.request_table.item(current_row, 0).text()
        new_date = self.request_table.item(current_row, 7).text()
        new_time = self.request_table.item(current_row, 8).text()
        new_room = self.request_table.item(current_row, 9).text()

        # 检查是否有冲突
        if self.check_exam_conflict(new_date, new_time, new_room):
            QMessageBox.warning(self, '冲突', '新的考试安排与现有安排冲突，无法通过')
            return

        try:
            # 更新考试安排
            update_arrangement_query = '''
                UPDATE exam_arrangements 
                SET 考试日期 = ?, 考试时间 = ?, 教室编号 = ?
                WHERE arrangement_id = (
                    SELECT arrangement_id FROM exam_adjustment_requests 
                    WHERE request_id = ?
                )
            '''
            self.db_manager.cursor.execute(update_arrangement_query, 
                                           (new_date, new_time, new_room, request_id))

            # 更新申请状态
            update_request_query = '''
                UPDATE exam_adjustment_requests 
                SET 状态 = '已同意', 审核人 = ?, 审核备注 = ?
                WHERE request_id = ?
            '''
            self.db_manager.cursor.execute(update_request_query, 
                                           ('管理员', '审核通过', request_id))

            self.db_manager.conn.commit()
            QMessageBox.information(self, '成功', '考场调整申请已通过')
            
            # 重新加载申请列表
            self.load_requests()

        except Exception as e:
            self.db_manager.conn.rollback()
            QMessageBox.warning(self, '错误', f'审核失败：{str(e)}')

    def reject_request(self):
        # 获取选中的申请
        current_row = self.request_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, '提示', '请选择要审核的申请')
            return

        # 获取申请ID
        request_id = self.request_table.item(current_row, 0).text()

        try:
            # 更新申请状态为已拒绝
            update_query = '''
                UPDATE exam_adjustment_requests 
                SET 状态 = '已拒绝', 审核人 = ?, 审核备注 = ?
                WHERE request_id = ?
            '''
            self.db_manager.cursor.execute(update_query, 
                                           ('管理员', '审核未通过', request_id))

            self.db_manager.conn.commit()
            QMessageBox.information(self, '成功', '考场调整申请已拒绝')
            
            # 重新加载申请列表
            self.load_requests()

        except Exception as e:
            self.db_manager.conn.rollback()
            QMessageBox.warning(self, '错误', f'操作失败：{str(e)}') 