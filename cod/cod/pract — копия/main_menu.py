# main_menu.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from db_connection import get_connection

class MainMenu(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user = user_data
        self.is_manager = (user_data['post_title'] == 'Заведующий аптекой')
        
        full_name = f"{user_data['surname']} {user_data['name']}"
        if user_data['middle_name']:
            full_name += f" {user_data['middle_name']}"
        
        self.setWindowTitle(f"Главное меню - {full_name}")
        self.resize(600, 600)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Шапка
        header = QLabel(f"👤 {self.user['surname']} {self.user['name']}\n📌 {self.user['post_title']}")
        header.setStyleSheet(f"background-color: #2c3e50; color: white; padding: 20px; font-size: 16px;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Статистика
        stats = self.get_statistics()
        stats_text = "\n".join(stats)
        stats_label = QLabel(f"📊 Статистика:\n{stats_text}")
        stats_label.setStyleSheet("background-color: white; padding: 15px; border-radius: 5px;")
        layout.addWidget(stats_label)
        
        # Кнопки для ВСЕХ
        btn_products = QPushButton("💊 Управление товарами")
        btn_products.setStyleSheet("background-color: #3498db; color: white; padding: 15px;")
        btn_products.clicked.connect(self.open_products)
        layout.addWidget(btn_products)
        
        if not self.is_manager:
            # Для фармацевта
            btn_expiry = QPushButton("⚠️ Контроль сроков")
            btn_expiry.setStyleSheet("background-color: #e67e22; color: white; padding: 15px;")
            btn_expiry.clicked.connect(self.open_expiry_control)
            layout.addWidget(btn_expiry)
            
            btn_writeoffs = QPushButton("📝 Списания")
            btn_writeoffs.setStyleSheet("background-color: #e74c3c; color: white; padding: 15px;")
            btn_writeoffs.clicked.connect(self.open_writeoffs)
            layout.addWidget(btn_writeoffs)
            
            btn_reports = QPushButton("📋 Просмотр отчетов")
            btn_reports.setStyleSheet("background-color: #3498db; color: white; padding: 15px;")
            btn_reports.clicked.connect(self.open_reports_view)
            layout.addWidget(btn_reports)
        else:
            # Для заведующего
            btn_reports = QPushButton("📊 Отчеты и экспорт в Word")
            btn_reports.setStyleSheet("background-color: #9b59b6; color: white; padding: 15px;")
            btn_reports.clicked.connect(self.open_reports)
            layout.addWidget(btn_reports)
        
        # Выход
        btn_logout = QPushButton("🚪 Выйти")
        btn_logout.setStyleSheet("background-color: #95a5a6; color: white; padding: 15px;")
        btn_logout.clicked.connect(self.logout)
        layout.addWidget(btn_logout)
        
        self.setLayout(layout)
    
    def get_statistics(self):
        conn = get_connection()
        if not conn:
            return ["Ошибка подключения"]
        
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM Product;")
            total = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM Product WHERE Expiration_date < CURRENT_DATE;")
            expired = cursor.fetchone()[0]
            return [f"Всего товаров: {total}", f"Просрочено: {expired}"]
        except:
            return ["Ошибка загрузки"]
        finally:
            cursor.close()
            conn.close()
    
    def open_products(self):
        from products_window import ProductsWindow
        self.products_window = ProductsWindow(self.user, full_access=True)
        self.products_window.show()
    
    def open_expiry_control(self):
        from expiry_control_window import ExpiryControlWindow
        self.expiry_window = ExpiryControlWindow(self.user)
        self.expiry_window.show()
    
    def open_writeoffs(self):
        from writeoffs_window import WriteoffsWindow
        self.writeoffs_window = WriteoffsWindow(self.user)
        self.writeoffs_window.show()
    
    def open_reports(self):
        from reports_window import ReportsWindow
        self.reports_window = ReportsWindow(self.user, can_export=True)
        self.reports_window.show()
    
    def open_reports_view(self):
        from reports_window import ReportsWindow
        self.reports_window = ReportsWindow(self.user, can_export=False)
        self.reports_window.show()
    
    def logout(self):
        from auth_window import AuthWindow
        self.auth_window = AuthWindow()
        self.auth_window.show()
        self.close()