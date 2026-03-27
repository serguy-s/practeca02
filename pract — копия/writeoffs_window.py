# writeoffs_window.py
from PyQt5.QtWidgets import (
    QMessageBox, QDialog, QVBoxLayout, QComboBox, 
    QSpinBox, QDateEdit, QLabel, QPushButton, QFormLayout,
    QTableWidgetItem, QHeaderView, QHBoxLayout
)
from base_table_window import QTableWidget
from PyQt5.QtCore import Qt, QDate
from db_connection import get_connection
from datetime import date
from base_table_window import TableWindow

class WriteoffsWindow(TableWindow):
    def __init__(self, user):
        columns = ["ID", "Товар", "Количество", "Дата", "Причина", "Кто списал"]
        super().__init__("Write_downs", columns, "📝 Списания", user)
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title = QLabel("📝 Оформление списания товаров")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            background-color: white;
            border-radius: 5px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Кнопка нового списания
        btn_layout = QHBoxLayout()
        
        self.btn_new = QPushButton("➕ Новое списание")
        self.btn_new.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 12px 25px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.btn_new.clicked.connect(self.on_add)
        btn_layout.addWidget(self.btn_new)
        
        btn_layout.addStretch()
        
        self.btn_refresh = QPushButton("🔄 Обновить список")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.btn_refresh.clicked.connect(self.load_data)
        btn_layout.addWidget(self.btn_refresh)
        
        layout.addLayout(btn_layout)
        
        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        
        self.load_data()
    
    def load_data(self):
        """Загрузка списаний"""
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к БД")
            return
        
        cursor = conn.cursor()
        try:
            # Исправленный запрос с правильными именами таблиц
            cursor.execute("""
                SELECT w.idWrite_downs, p.Title, w.Quantity, w.Date, w.Reason, 
                       u.surname || ' ' || u.name as user_name
                FROM Write_downs w
                JOIN Product p ON w.IDProduct = p.idProduct
                JOIN "user" u ON w.IDUser = u.idUser
                ORDER BY w.Date DESC;
            """)
            data = cursor.fetchall()
            
            self.table.setRowCount(len(data))
            for row_idx, row in enumerate(data):
                for col_idx, value in enumerate(row):
                    if value is None:
                        item = QTableWidgetItem("")
                    elif col_idx == 3:  # date
                        if isinstance(value, date):
                            item = QTableWidgetItem(value.strftime("%d.%m.%Y"))
                        else:
                            item = QTableWidgetItem(str(value))
                    else:
                        item = QTableWidgetItem(str(value))
                    self.table.setItem(row_idx, col_idx, item)
                    
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки:\n{str(e)}")
            print(f"Ошибка загрузки: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def on_add(self):
        """Добавление списания"""
        dialog = WriteoffDialog(self.user, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()
            QMessageBox.information(self, "Успех", "Списание оформлено!")


class WriteoffDialog(QDialog):
    """Диалог списания"""
    
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Оформление списания")
        self.resize(450, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f8ff;
            }
            QLabel {
                font-weight: bold;
                color: #2c3e50;
            }
            QComboBox, QSpinBox, QDateEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        self.init_ui()
        self.load_products()
    
    def load_products(self):
        """Загрузка списка товаров"""
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к БД")
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT idProduct, Title, Quantity, Expiration_date 
                FROM Product 
                WHERE Quantity > 0 
                ORDER BY Title;
            """)
            self.products = cursor.fetchall()
            
            self.combo_product.clear()
            for prod in self.products:
                days_left = (prod[3] - date.today()).days if prod[3] else 0
                status = "❌ ПРОСРОЧЕНО" if days_left < 0 else f"(в наличии: {prod[2]})"
                self.combo_product.addItem(
                    f"{prod[1]} {status}",
                    prod[0]
                )
                
            if self.products:
                self.check_quantity()
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки товаров:\n{str(e)}")
            print(f"Ошибка загрузки товаров: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title = QLabel("✏️ Оформление акта списания")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #e74c3c;
            padding: 10px;
            background-color: #fdedec;
            border-radius: 5px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        form = QFormLayout()
        form.setSpacing(15)
        
        # Товар
        self.combo_product = QComboBox()
        self.combo_product.currentIndexChanged.connect(self.check_quantity)
        form.addRow("📦 Товар:", self.combo_product)
        
        # Количество
        self.spin_quantity = QSpinBox()
        self.spin_quantity.setRange(1, 9999)
        self.spin_quantity.valueChanged.connect(self.check_quantity)
        form.addRow("🔢 Количество:", self.spin_quantity)
        
        # Причина
        self.combo_reason = QComboBox()
        reasons = ['Истек срок годности', 'Брак упаковки', 'Повреждение', 'Возврат поставщику', 'Другое']
        self.combo_reason.addItems(reasons)
        form.addRow("📝 Причина:", self.combo_reason)
        
        # Дата
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form.addRow("📅 Дата:", self.date_edit)
        
        layout.addLayout(form)
        
        # Информация об остатке
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("""
            color: #27ae60;
            padding: 10px;
            background-color: #e8f8f5;
            border-radius: 5px;
            font-weight: bold;
        """)
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        
        btn_save = QPushButton("✅ Оформить списание")
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 12px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_save.clicked.connect(self.save_writeoff)
        btn_layout.addWidget(btn_save)
        
        btn_cancel = QPushButton("✖ Отмена")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def check_quantity(self):
        """Проверка остатка"""
        if self.combo_product.count() > 0 and self.products:
            current_index = self.combo_product.currentIndex()
            if 0 <= current_index < len(self.products):
                product = self.products[current_index]
                self.info_label.setText(f"✅ В наличии: {product[2]} шт.")
                
                if self.spin_quantity.value() > product[2]:
                    self.info_label.setStyleSheet("""
                        color: #e74c3c;
                        padding: 10px;
                        background-color: #fadbd8;
                        border-radius: 5px;
                        font-weight: bold;
                    """)
                else:
                    self.info_label.setStyleSheet("""
                        color: #27ae60;
                        padding: 10px;
                        background-color: #e8f8f5;
                        border-radius: 5px;
                        font-weight: bold;
                    """)
    
    def save_writeoff(self):
        """Сохранение списания"""
        if self.combo_product.count() == 0:
            QMessageBox.warning(self, "Ошибка", "Нет товаров для списания")
            return
        
        product_id = self.combo_product.currentData()
        quantity = self.spin_quantity.value()
        reason = self.combo_reason.currentText()
        writeoff_date = self.date_edit.date().toPyDate()
        
        # Проверяем остаток
        current_index = self.combo_product.currentIndex()
        if 0 <= current_index < len(self.products):
            product = self.products[current_index]
            if quantity > product[2]:
                QMessageBox.warning(self, "Ошибка", 
                    f"Недостаточно товара! В наличии: {product[2]}")
                return
        
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к БД")
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("BEGIN;")
            
            # Добавляем списание
            cursor.execute("""
                INSERT INTO Write_downs (IDProduct, IDUser, Quantity, Date, Reason)
                VALUES (%s, %s, %s, %s, %s);
            """, (product_id, self.user['id'], quantity, writeoff_date, reason))
            
            # Уменьшаем количество товара
            cursor.execute("""
                UPDATE Product SET Quantity = Quantity - %s 
                WHERE idProduct = %s;
            """, (quantity, product_id))
            
            conn.commit()
            QMessageBox.information(self, "Успех", "Списание успешно оформлено!")
            self.accept()
            
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка списания:\n{str(e)}")
            print(f"Ошибка списания: {e}")
        finally:
            cursor.close()
            conn.close()