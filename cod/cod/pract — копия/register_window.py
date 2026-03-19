# register_window.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QComboBox,
    QHBoxLayout, QGroupBox
)
from PyQt5.QtCore import Qt
from db_connection import get_connection

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация сотрудника")
        self.resize(450, 550)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f8ff;
            }
            QLineEdit, QComboBox {
                padding: 10px;
                border: 2px solid #b0c4de;
                border-radius: 5px;
                font-size: 14px;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #b0c4de;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        self.load_posts()
        self.init_ui()
    
    def load_posts(self):
        """Загрузка списка должностей из таблицы Post"""
        self.posts = []
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT idPost, title FROM Post ORDER BY title;")
                self.posts = cursor.fetchall()
            except Exception as e:
                print(f"Ошибка загрузки должностей: {e}")
                self.posts = [(1, "Фармацевт"), (2, "Заведующий аптекой")]
            finally:
                cursor.close()
                conn.close()
        else:
            self.posts = [(1, "Фармацевт"), (2, "Заведующий аптекой")]
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # Заголовок
        title = QLabel("📝 Регистрация нового сотрудника")
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
        
        # Группа ФИО
        fio_group = QGroupBox("ФИО сотрудника")
        fio_layout = QVBoxLayout()
        
        fio_layout.addWidget(QLabel("Фамилия*:"))
        self.input_surname = QLineEdit()
        self.input_surname.setPlaceholderText("Введите фамилию")
        fio_layout.addWidget(self.input_surname)
        
        fio_layout.addWidget(QLabel("Имя*:"))
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Введите имя")
        fio_layout.addWidget(self.input_name)
        
        fio_layout.addWidget(QLabel("Отчество:"))
        self.input_middlename = QLineEdit()
        self.input_middlename.setPlaceholderText("Введите отчество (необязательно)")
        fio_layout.addWidget(self.input_middlename)
        
        fio_group.setLayout(fio_layout)
        layout.addWidget(fio_group)
        
        # Группа учетные данные
        auth_group = QGroupBox("Учетные данные")
        auth_layout = QVBoxLayout()
        
        auth_layout.addWidget(QLabel("Логин*:"))
        self.input_login = QLineEdit()
        self.input_login.setPlaceholderText("Введите логин")
        auth_layout.addWidget(self.input_login)
        
        auth_layout.addWidget(QLabel("Пароль*:"))
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Введите пароль")
        self.input_password.setEchoMode(QLineEdit.Password)
        auth_layout.addWidget(self.input_password)
        
        auth_layout.addWidget(QLabel("Подтверждение*:"))
        self.input_confirm = QLineEdit()
        self.input_confirm.setPlaceholderText("Повторите пароль")
        self.input_confirm.setEchoMode(QLineEdit.Password)
        auth_layout.addWidget(self.input_confirm)
        
        auth_group.setLayout(auth_layout)
        layout.addWidget(auth_group)
        
        # Группа должность
        post_group = QGroupBox("Должность")
        post_layout = QVBoxLayout()
        
        self.combo_post = QComboBox()
        for post_id, post_title in self.posts:
            self.combo_post.addItem(post_title, post_id)
        post_layout.addWidget(self.combo_post)
        
        post_group.setLayout(post_layout)
        layout.addWidget(post_group)
        
        # Информация
        info = QLabel("* - обязательные поля")
        info.setStyleSheet("color: #e74c3c; font-size: 11px;")
        layout.addWidget(info)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        
        self.btn_register = QPushButton("✅ Зарегистрироваться")
        self.btn_register.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.btn_register.clicked.connect(self.register_user)
        btn_layout.addWidget(self.btn_register)
        
        self.btn_cancel = QPushButton("✖ Отмена")
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.btn_cancel.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def register_user(self):
        """Регистрация пользователя"""
        # Получаем данные
        surname = self.input_surname.text().strip()
        name = self.input_name.text().strip()
        middlename = self.input_middlename.text().strip() or None
        username = self.input_login.text().strip()
        password = self.input_password.text().strip()
        confirm = self.input_confirm.text().strip()
        post_id = self.combo_post.currentData()
        post_title = self.combo_post.currentText()
        
        # Проверка
        if not all([surname, name, username, password, confirm]):
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля!")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают!")
            return
        
        if len(username) < 3:
            QMessageBox.warning(self, "Ошибка", "Логин должен быть минимум 3 символа")
            return
        
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к БД")
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("BEGIN;")
            
            # Проверка существования
            cursor.execute('SELECT idUser FROM "user" WHERE login = %s;', (username,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Ошибка", "Пользователь уже существует!")
                return
            
            # Создаем пользователя
            cursor.execute('''
                INSERT INTO "user" (surname, name, middle_name, login, password, idPost)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING idUser;
            ''', (surname, name, middlename, username, password, post_id))
            
            user_id = cursor.fetchone()[0]
            
            conn.commit()
            
            QMessageBox.information(self, "Успех", 
                f"✅ Сотрудник зарегистрирован!\n\n"
                f"ФИО: {surname} {name} {middlename or ''}\n"
                f"Должность: {post_title}\n"
                f"Логин: {username}")
            
            self.close()
            
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка регистрации:\n{str(e)}")
            print(f"Ошибка: {e}")
        finally:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RegisterWindow()
    window.show()
    sys.exit(app.exec_())