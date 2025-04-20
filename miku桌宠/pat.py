import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel,QPushButton
)
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QMovie
import os


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        # 如果是打包后的环境
        base_path = sys._MEIPASS
    else:
        # 开发环境，直接使用当前路径
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

class PetWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.start_movie = QMovie(resource_path("img2/1.gif"))
        self.normal_movie = QMovie(resource_path("img2/normal2.gif"))
        self.shy_movie = QMovie(resource_path("img2/feiwen.gif"))
        self.eating_movie = QMovie(resource_path("img2/kaixin.gif"))
        self.sleeping_movie = QMovie(resource_path("img2/shuijiao.gif"))
        self.dragging_movie = QMovie(resource_path("img2/haipa.gif"))
        
        self.size_width = 300
        self.size_height = 300
        self.setFixedSize(self.size_width,self.size_height)

        #初始化
        self.start_movie.start()
        self.setMovie(self.start_movie)
        self.tim = QTimer(self)
        self.tim.timeout.connect(self.reset_expression)
        self.tim.start(2000)  # 2秒后开始
        self.tim.setSingleShot(True)  # 设置为单次触发
        
        self.is_shy = False 
        self.is_eating = False
        self.is_sleeping = False
        self.is_dragging = False
        self.drag_start_position = QPoint()

        # 定时器，用于恢复表情
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.reset_expression)
        self.timer.setInterval(5000)  # 5秒后恢复
        
        #初始化点击时长
        self.click_start_time = None
        
        #用于记录点击位置
        self.click_pos = QPoint()
        self.is_move = False
        
        self.right_count = 0
        self.btn = False
    def resizeEvent(self, event):
        super().resizeEvent(event)  # 调用父类的 resizeEvent 方法
        self.normal_movie.setScaledSize(self.size())
        self.shy_movie.setScaledSize(0.95*self.size())
        self.eating_movie.setScaledSize(0.95*self.size())
        self.sleeping_movie.setScaledSize(0.85*self.size())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # 记录点击位置
            self.click_pos = event.globalPosition().toPoint()
            pos = self.parent().pos()
            # 记录点击开始时间
            self.click_start_time = event.timestamp()
            # 记录拖动开始位置
            self.drag_start_position = event.globalPosition().toPoint() - self.parent().pos()
            self.is_dragging = False
            if pos.y()<self.click_pos.y()<pos.y()+self.size_height*0.5: #and pos.x()+self.size_width*0.4<self.click_pos.x()<pos.x()+self.size_width*0.6
                self.is_move = True
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.right_count += 1
            if self.right_count == 1:
                self.btn = True
            elif self.right_count == 2:
                self.btn = False
                self.right_count = 0
            
            self.parent().update_buttons(self.btn) # 通知父窗口更新按钮状态
            event.accept()
                 
    def mouseMoveEvent(self, event):
        if self.is_move:
            if event.buttons() & Qt.MouseButton.LeftButton:
                current_time = event.timestamp()
                if current_time - self.click_start_time > 200:
                        self.is_dragging = True
                        new_pos =event.globalPosition().toPoint() - self.drag_start_position
                        self.parent().move(new_pos)
                        self.parent().update_button_positions()
                        self.switch_to_dragging()
            event.accept()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.click_start_time:
                click_duration = event.timestamp() - self.click_start_time
                if click_duration < 200:
                    if not self.is_eating and not self.is_sleeping:
                        self.switch_to_shy()
                else:
                    self.reset_expression()
            #重置状态
            self.click_start_time = None
            self.is_dragging = False
            self.is_move = False
            event.accept()

    def reset_expression(self):
        self.switch_to_normal()
        self.timer.stop()
    
    def switch_to_normal(self):
        self.stop_all_movies()
        self.normal_movie.start()
        self.setMovie(self.normal_movie)
        self.is_shy = False
        self.is_eating = False
        self.is_sleeping = False

    def switch_to_shy(self):
        self.stop_all_movies()
        self.shy_movie.start()
        self.setMovie(self.shy_movie)
        self.is_shy = True
        self.timer.start()

    def switch_to_eating(self):
        self.stop_all_movies()
        self.eating_movie.start()
        self.setMovie(self.eating_movie)
        self.is_eating = True
        self.timer.start()
    def switch_to_dragging(self):
        self.stop_all_movies()
        self.dragging_movie.start()
        self.setMovie(self.dragging_movie)
        self.is_dragging = True

    def switch_to_sleeping(self):
        self.stop_all_movies()
        self.sleeping_movie.start()
        self.setMovie(self.sleeping_movie)
        self.is_sleeping = True
        self.timer.start()

    def stop_all_movies(self):
        self.normal_movie.stop()
        self.shy_movie.stop()
        self.eating_movie.stop()
        self.sleeping_movie.stop()
        self.update()
    def eat(self):
        self.switch_to_eating()
    
    def sleep(self):
        self.switch_to_sleeping()


class PetButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(80, 30)
        self.setStyleSheet("""
            QPushButton {
                background-color: lightblue;
                color: darkblue;
                font-size: 14px;
                border: 2px solid darkblue;
                border-radius: 10px;
                padding: 5px 10px;
            }
        """)


class PetApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        self.setWindowTitle("桌宠")
        self.setGeometry(1300,500,300,330)
         #设置窗口标志
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowSystemMenuHint | Qt.WindowType.WindowStaysOnTopHint )
        # 设置背景透明
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # 创建宠物
        self.pet = PetWidget(self)
        self.pet.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #创建按钮
        self.eat_button = PetButton("开心", self)
        self.eat_button.clicked.connect(self.on_eat_clicked)
        self.eat_button.hide()  # 默认隐藏
        
        self.sleep_button = PetButton("睡觉", self)
        self.sleep_button.clicked.connect(self.on_sleep_clicked)
        self.sleep_button.hide()

        self.quit_button = PetButton("quit",self)
        self.quit_button.clicked.connect(self.on_quit_clicked)
        self.quit_button.hide()
        
        #初始化按钮位置
        self.update_button_positions()  
        
    def on_eat_clicked(self):
        self.pet.eat()
    
    def on_sleep_clicked(self):
        self.pet.sleep()
        
    def on_quit_clicked(self):
        self.close()
    
    def update_buttons(self, show):
        if show:
            self.eat_button.show()
            self.sleep_button.show()
            self.quit_button.show()
        else:
            self.eat_button.hide()
            self.sleep_button.hide()
            self.quit_button.hide()
    def update_button_positions(self):
        # 更新按钮位置
        button_offset_1 = QPoint(30, self.pet.size_height)  # 按钮相对于宠物的偏移量
        button_offset_2 = QPoint(115, self.pet.size_height)
        button_offset_3 = QPoint(200, self.pet.size_height)
        self.eat_button.move(self.pet.pos() + button_offset_1)
        self.sleep_button.move(self.pet.pos() + button_offset_2)
        self.quit_button.move(self.pet.pos() + button_offset_3)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet_app = PetApp()
    pet_app.show()
    sys.exit(app.exec())
