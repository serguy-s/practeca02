# change_password_window.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from db_connection import get_connection
import hashlib

class ChangePasswordWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Смена пароля")
        self.resize(400, 300)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f8ff;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #b0c4de;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton {
                padding: 12px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Заголовок
        title = QLabel("🔐 Смена пароля")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            padding: 15px;
            background-color: #e6f3ff;
            border-radius: 8px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Информация о пользователе
        info_label = QLabel(f"Пользователь: {self.user['surname']} {self.user['name']}")
        info_label.setStyleSheet("color: #34495e; font-size: 14px; padding: 5px;")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        layout.addSpacing(10)
        
        # Старый пароль
        layout.addWidget(QLabel("Текущий пароль:"))
        self.old_password = QLineEdit()
        self.old_password.setEchoMode(QLineEdit.Password)
        self.old_password.setPlaceholderText("Введите текущий пароль")
        layout.addWidget(self.old_password)
        
        # Новый пароль
        layout.addWidget(QLabel("Новый пароль:"))
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setPlaceholderText("Введите новый пароль (мин. 4 символа)")
        layout.addWidget(self.new_password)
        
        # Подтверждение
        layout.addWidget(QLabel("Подтверждение:"))
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setPlaceholderText("Повторите новый пароль")
        layout.addWidget(self.confirm_password)
        
        layout.addSpacing(10)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        
        self.btn_save = QPushButton("✅ Сохранить")
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.btn_save.clicked.connect(self.change_password)
        btn_layout.addWidget(self.btn_save)
        
        self.btn_cancel = QPushButton("✖ Отмена")
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.btn_cancel.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def change_password(self):
        """Смена пароля"""
        old_pass = self.old_password.text().strip()
        new_pass = self.new_password.text().strip()
        confirm = self.confirm_password.text().strip()
        
        if not old_pass or not new_pass or not confirm:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return
        
        if new_pass != confirm:
            QMessageBox.warning(self, "Ошибка", "Новые пароли не совпадают!")
            return
        
        if len(new_pass) < 4:
            QMessageBox.warning(self, "Ошибка", "Пароль должен быть минимум 4 символа!")
            return
        
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к БД")
            return
        
        cursor = conn.cursor()
        try:
            # Проверяем старый пароль
            cursor.execute('SELECT password FROM "user" WHERE idUser = %s;', (self.user['id'],))
            current_pass = cursor.fetchone()
            
            if not current_pass:
                QMessageBox.critical(self, "Ошибка", "Пользователь не найден")
                return
            
            # В вашей БД пароль хранится в открытом виде
            if old_pass != current_pass[0]:
                QMessageBox.warning(self, "Ошибка", "Неверный текущий пароль!")
                return
            
            # Обновляем пароль
            cursor.execute('UPDATE "user" SET password = %s WHERE idUser = %s;', 
                         (new_pass, self.user['id']))
            conn.commit()
            
            QMessageBox.information(self, "Успех", "Пароль успешно изменен!")
            self.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при смене пароля:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()