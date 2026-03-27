# expiry_control_window.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QHeaderView, QTabWidget, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush
from db_connection import get_connection
from datetime import date, timedelta

class ExpiryControlWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("⚠️ Контроль сроков годности")
        self.resize(900, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f4f8;
            }
            QTabWidget::pane {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 10px;
            }
            QTabBar::tab {
                padding: 10px 20px;
                font-weight: bold;
            }
        """)
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title = QLabel("⚠️ Контроль сроков годности лекарств")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            padding: 15px;
            background-color: white;
            border-radius: 8px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Вкладки
        self.tabs = QTabWidget()
        
        # Вкладка с просроченными
        self.expired_tab = QWidget()
        self.create_expired_tab()
        self.tabs.addTab(self.expired_tab, "❌ Просроченные")
        
        # Вкладка с истекающими (10 дней)
        self.critical_tab = QWidget()
        self.create_critical_tab()
        self.tabs.addTab(self.critical_tab, "⚠️ Критичные (≤10 дней)")
        
        # Вкладка с истекающими (30 дней)
        self.warning_tab = QWidget()
        self.create_warning_tab()
        self.tabs.addTab(self.warning_tab, "⚠️ Скоро истекают (≤30 дней)")
        
        layout.addWidget(self.tabs)
        
        # Кнопка обновления
        btn_refresh = QPushButton("🔄 Обновить данные")
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_refresh.clicked.connect(self.load_data)
        layout.addWidget(btn_refresh)
        
        self.setLayout(layout)
    
    def create_expired_tab(self):
        """Создание вкладки с просроченными"""
        layout = QVBoxLayout(self.expired_tab)
        
        self.expired_table = QTableWidget()
        self.expired_table.setColumnCount(6)
        self.expired_table.setHorizontalHeaderLabels(
            ["ID", "Название", "Производитель", "Срок годности", "Количество", "Дней просрочено"]
        )
        self.expired_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.expired_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.expired_table)
    
    def create_critical_tab(self):
        """Создание вкладки с критичными (≤10 дней)"""
        layout = QVBoxLayout(self.critical_tab)
        
        self.critical_table = QTableWidget()
        self.critical_table.setColumnCount(6)
        self.critical_table.setHorizontalHeaderLabels(
            ["ID", "Название", "Производитель", "Срок годности", "Количество", "Осталось дней"]
        )
        self.critical_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.critical_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.critical_table)
    
    def create_warning_tab(self):
        """Создание вкладки с предупреждением (≤30 дней)"""
        layout = QVBoxLayout(self.warning_tab)
        
        self.warning_table = QTableWidget()
        self.warning_table.setColumnCount(6)
        self.warning_table.setHorizontalHeaderLabels(
            ["ID", "Название", "Производитель", "Срок годности", "Количество", "Осталось дней"]
        )
        self.warning_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.warning_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.warning_table)
    
    def load_data(self):
        """Загрузка данных из таблицы Product"""
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к БД")
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT idProduct, Title, Manufacturer, Expiration_date, Quantity 
                FROM Product 
                ORDER BY Expiration_date;
            """)
            products = cursor.fetchall()
            
            today = date.today()
            
            expired = []
            critical = []
            warning = []
            
            for prod in products:
                if prod[3]:  # если есть дата
                    days_left = (prod[3] - today).days
                    
                    if days_left < 0:
                        expired.append((*prod, abs(days_left)))
                    elif days_left <= 10:
                        critical.append((*prod, days_left))
                    elif days_left <= 30:
                        warning.append((*prod, days_left))
            
            # Заполняем таблицы
            self.fill_table(self.expired_table, expired, True)
            self.fill_table(self.critical_table, critical, False)
            self.fill_table(self.warning_table, warning, False)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    def fill_table(self, table, data, is_expired):
        """Заполнение таблицы"""
        table.setRowCount(len(data))
        
        for row, item in enumerate(data):
            # ID
            table.setItem(row, 0, QTableWidgetItem(str(item[0])))
            # Название
            table.setItem(row, 1, QTableWidgetItem(item[1]))
            # Производитель
            table.setItem(row, 2, QTableWidgetItem(item[2]))
            # Срок годности
            if item[3]:
                table.setItem(row, 3, QTableWidgetItem(item[3].strftime("%d.%m.%Y")))
            else:
                table.setItem(row, 3, QTableWidgetItem(""))
            # Количество
            table.setItem(row, 4, QTableWidgetItem(str(item[4])))
           
            # Дни
            days_item = QTableWidgetItem(str(item[5]))
            if is_expired:
                days_item.setText(f"{item[5]} дн. просрочено")
                days_item.setForeground(QBrush(QColor("#e74c3c")))
            else:
                days_item.setText(f"{item[5]} дн.")
                if item[5] <= 10:
                    days_item.setForeground(QBrush(QColor("#e67e22")))
                else:
                    days_item.setForeground(QBrush(QColor("#f39c12")))
            
            table.setItem(row, 5, days_item)