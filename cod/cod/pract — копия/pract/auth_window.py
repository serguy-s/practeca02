# auth_window.py
import sys
import hashlib
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QHBoxLayout,
    QDialog
)
from PyQt5.QtCore import Qt
from db_connection import get_connection
from register_window import RegisterWindow
from main_menu import MainMenu
from change_password_window import ChangePasswordWindow

class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация - Аптека")
        self.resize(400, 320)  # Уменьшил размер
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
        layout.setContentsMargins(40, 30, 40, 30)
        
        # Заголовок
        title = QLabel("💊 Аптечная информационная система")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            padding: 20px;
            background-color: #e6f3ff;
            border-radius: 10px;
        """)
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Поле логина
        layout.addWidget(QLabel("👤 Логин:"))
        self.input_login = QLineEdit()
        self.input_login.setPlaceholderText("Введите логин")
        layout.addWidget(self.input_login)
        
        # Поле пароля
        layout.addWidget(QLabel("🔒 Пароль:"))
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Введите пароль")
        self.input_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input_password)
        
        layout.addSpacing(10)
        
        # Кнопки входа и регистрации
        buttons_layout = QHBoxLayout()
        
        self.btn_login = QPushButton("🚪 Войти")
        self.btn_login.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.btn_login.clicked.connect(self.check_login)
        buttons_layout.addWidget(self.btn_login)
        
        self.btn_register = QPushButton("📝 Регистрация")
        self.btn_register.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.btn_register.clicked.connect(self.show_register)
        buttons_layout.addWidget(self.btn_register)
        
        layout.addLayout(buttons_layout)
        
        # Кнопка "Забыли пароль?"
        self.btn_forgot = QPushButton("❓ Забыли пароль?")
        self.btn_forgot.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3498db;
                border: none;
                font-size: 12px;
                text-decoration: underline;
                padding: 5px;
            }
            QPushButton:hover {
                color: #2980b9;
            }
        """)
        self.btn_forgot.clicked.connect(self.show_password_recovery)
        layout.addWidget(self.btn_forgot)
        
        self.setLayout(layout)

    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()

    def check_login(self):
        """Проверка логина"""
        username = self.input_login.text().strip()
        password = self.input_password.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль!")
            return
        
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к БД")
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT u.idUser, u.login, u.password, u.surname, u.name, u.middle_name, 
                       p.title, p.idPost
                FROM "user" u
                LEFT JOIN Post p ON u.idPost = p.idPost
                WHERE u.login = %s;
            ''', (username,))
            
            user = cursor.fetchone()
            
            if not user:
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
                return
            
            if password == user[2]:
                user_data = {
                    'id': user[0],
                    'login': user[1],
                    'surname': user[3] or '',
                    'name': user[4] or '',
                    'middle_name': user[5] or '',
                    'post_title': user[6] or 'Не указана',
                    'post_id': user[7]
                }
                
                full_name = f"{user_data['surname']} {user_data['name']}"
                if user_data['middle_name']:
                    full_name += f" {user_data['middle_name']}"
                
                QMessageBox.information(self, "Успех", 
                    f"Добро пожаловать, {full_name}!\nДолжность: {user_data['post_title']}")
                
                self.open_main_menu(user_data)
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный пароль!")
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при входе:\n{str(e)}")
            print(f"Ошибка: {e}")
        finally:
            cursor.close()
            conn.close()

    def show_register(self):
        """Открыть окно регистрации"""
        self.register_window = RegisterWindow()
        self.register_window.show()

    def show_password_recovery(self):
        """Показать окно восстановления пароля"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Восстановление пароля")
        dialog.resize(400, 250)
        
        layout = QVBoxLayout(dialog)
        
        # Заголовок
        title = QLabel("🔐 Восстановление пароля")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Поле логина
        layout.addWidget(QLabel("Введите ваш логин:"))
        input_login = QLineEdit()
        input_login.setPlaceholderText("Логин")
        layout.addWidget(input_login)
        
        # Поле фамилии для подтверждения
        layout.addWidget(QLabel("Введите вашу фамилию:"))
        input_surname = QLineEdit()
        input_surname.setPlaceholderText("Фамилия")
        layout.addWidget(input_surname)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        
        btn_recover = QPushButton("✅ Восстановить")
        btn_recover.setStyleSheet("background-color: #27ae60; color: white; padding: 10px;")
        btn_recover.clicked.connect(lambda: self.recover_password(dialog, input_login.text(), input_surname.text()))
        btn_layout.addWidget(btn_recover)
        
        btn_cancel = QPushButton("✖ Отмена")
        btn_cancel.setStyleSheet("background-color: #95a5a6; color: white; padding: 10px;")
        btn_cancel.clicked.connect(dialog.reject)
        btn_layout.addWidget(btn_cancel)
        
        layout.addLayout(btn_layout)
        
        dialog.exec_()
    
    def recover_password(self, dialog, login, surname):
        """Восстановление пароля"""
        if not login or not surname:
            QMessageBox.warning(dialog, "Ошибка", "Заполните все поля!")
            return
        
        conn = get_connection()
        if not conn:
            QMessageBox.critical(dialog, "Ошибка", "Не удалось подключиться к БД")
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT u.password, u.surname 
                FROM "user" u
                WHERE u.login = %s;
            ''', (login,))
            
            user = cursor.fetchone()
            
            if not user:
                QMessageBox.warning(dialog, "Ошибка", "Пользователь не найден!")
                return
            
            if user[1].lower() != surname.lower():
                QMessageBox.warning(dialog, "Ошибка", "Фамилия не совпадает!")
                return
            
            QMessageBox.information(dialog, "Ваш пароль", 
                f"Логин: {login}\nПароль: {user[0]}\n\nРекомендуем сменить пароль после входа!")
            
            dialog.accept()
            
        except Exception as e:
            QMessageBox.critical(dialog, "Ошибка", f"Ошибка: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def open_main_menu(self, user_data):
        """Открыть главное меню"""
        self.main_menu = MainMenu(user_data)
        self.main_menu.show()
        self.hide()
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AuthWindow()
    window.show()
    sys.exit(app.exec_())