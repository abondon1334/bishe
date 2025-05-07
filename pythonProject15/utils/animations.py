from PyQt5.QtCore import QPropertyAnimation, QEasingCurve

def fade_in_animation(widget, duration=500):
    widget.setWindowOpacity(0)
    widget.show()
    
    animation = QPropertyAnimation(widget, b"windowOpacity")
    animation.setDuration(duration)
    animation.setStartValue(0)
    animation.setEndValue(1)
    animation.setEasingCurve(QEasingCurve.InOutQuad)
    animation.start()

def hover_animation(widget):
    """为按钮添加悬停缩放效果"""
    widget.enterEvent = lambda event: widget.setStyleSheet(
        f"transform: scale(1.05); background-color: {COLORS['secondary']};"
    )
    widget.leaveEvent = lambda event: widget.setStyleSheet(
        f"transform: scale(1.0); background-color: {COLORS['primary']};"
    ) 