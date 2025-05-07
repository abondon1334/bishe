from PyQt5.QtGui import QColor

# 颜色定义
COLORS = {
    'primary': '#3498db',     # 主蓝色
    'secondary': '#2980b9',   # 深蓝色
    'background': '#f4f6f7',  # 浅灰背景
    'text_dark': '#2c3e50',   # 深灰文字
    'text_light': '#000000',  # 黑色文字
    'border': '#bdc3c7',      # 边框灰色
    'button_bg': '#ffffff'    # 按钮背景白色
}

# 通用样式表
GLOBAL_STYLESHEET = f"""
    * {{
        font-family: 'Microsoft YaHei', Arial, sans-serif;
        transition: all 0.3s ease;
    }}
    QWidget {{
        background-color: {COLORS['background']};
    }}
    QLabel {{
        color: {COLORS['text_dark']};
    }}
    QPushButton {{
        background-color: {COLORS['button_bg']};
        color: {COLORS['text_dark']};
        border: 2px solid {COLORS['primary']};
        padding: 10px 20px;
        border-radius: 15px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {COLORS['primary']};
        color: {COLORS['button_bg']};
        transform: scale(1.05);
    }}
    QPushButton:pressed {{
        background-color: {COLORS['secondary']};
        color: {COLORS['button_bg']};
    }}
"""

def add_shadow_effect(widget, color=QColor(0, 0, 0, 80), blur_radius=20, offset=(0, 10)):
    from PyQt5.QtWidgets import QGraphicsDropShadowEffect
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur_radius)
    shadow.setColor(color)
    shadow.setOffset(*offset)
    widget.setGraphicsEffect(shadow) 