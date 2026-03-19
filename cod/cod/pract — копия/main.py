# main.py
import sys
from PyQt5.QtWidgets import QApplication
from auth_window import AuthWindow
from db_connection import init_database

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Проверка подключения к БД
    if not init_database():
        print("❌ Ошибка подключения к базе данных!")
        sys.exit(1)
    
    # Запуск
    auth_window = AuthWindow()
    auth_window.show()
    
    sys.exit(app.exec_())