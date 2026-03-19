# base_table_window.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLineEdit, QLabel,
    QMessageBox, QHeaderView, QDialog, QFormLayout,
    QDialogButtonBox, QDateEdit, QDoubleSpinBox, QSpinBox,
    QComboBox
)
from PyQt5.QtCore import Qt, QDate
from db_connection import get_connection

class TableWindow(QWidget):
    """Базовый класс для окон с таблицами"""
    
    def __init__(self, table_name, columns, window_title, user=None):
        super().__init__()
        self.table_name = table_name
        self.columns = columns
        self.user = user
        self.is_manager = user and user.get('post_title') == 'Заведующий аптекой' if user else False
        
        self.setWindowTitle(window_title)
        self.resize(900, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f4f8;
            }
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                gridline-color: #dee2e6;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton {
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Поиск
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 Поиск:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите текст для поиска...")
        self.search_input.textChanged.connect(self.search_data)
        self.search_input.setStyleSheet("padding: 8px; border: 2px solid #bdc3c7; border-radius: 5px;")
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.doubleClicked.connect(self.on_double_click)
        layout.addWidget(self.table)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        self.btn_add = QPushButton("➕ Добавить")
        self.btn_add.setStyleSheet("background-color: #2ecc71; color: white;")
        self.btn_add.clicked.connect(self.on_add)
        buttons_layout.addWidget(self.btn_add)
        
        self.btn_edit = QPushButton("✏️ Редактировать")
        self.btn_edit.setStyleSheet("background-color: #f39c12; color: white;")
        self.btn_edit.clicked.connect(self.on_edit)
        buttons_layout.addWidget(self.btn_edit)
        
        self.btn_delete = QPushButton("🗑️ Удалить")
        self.btn_delete.setStyleSheet("background-color: #e74c3c; color: white;")
        self.btn_delete.clicked.connect(self.on_delete)
        buttons_layout.addWidget(self.btn_delete)
        
        self.btn_refresh = QPushButton("🔄 Обновить")
        self.btn_refresh.setStyleSheet("background-color: #3498db; color: white;")
        self.btn_refresh.clicked.connect(self.load_data)
        buttons_layout.addWidget(self.btn_refresh)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def load_data(self):
        """Загрузка данных из БД - исправлено для таблицы Product"""
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к БД")
            return
        
        cursor = conn.cursor()
        try:
            # Для таблицы Product используем сортировку по idProduct
            if self.table_name == "Product":
                cursor.execute(f"SELECT * FROM {self.table_name} ORDER BY idProduct;")
            else:
                cursor.execute(f"SELECT * FROM {self.table_name} ORDER BY id;")
            
            data = cursor.fetchall()
            
            self.table.setRowCount(len(data))
            for row_idx, row in enumerate(data):
                for col_idx, value in enumerate(row):
                    if value is None:
                        item = QTableWidgetItem("")
                    else:
                        item = QTableWidgetItem(str(value))
                    
                    # Специальная обработка для дат
                    if col_idx < len(self.columns) and ('date' in self.columns[col_idx].lower() or 'годности' in self.columns[col_idx].lower()):
                        from datetime import date
                        if isinstance(value, date):
                            item = QTableWidgetItem(value.strftime("%d.%m.%Y"))
                    
                    self.table.setItem(row_idx, col_idx, item)
                    
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    def search_data(self):
        """Поиск по таблице"""
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)
    
    def get_selected_row(self):
        """Получить выбранную строку"""
        current_row = self.table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись")
            return None
        return current_row
    
    def get_row_data(self, row):
        """Получить данные строки"""
        data = {}
        for col in range(self.table.columnCount()):
            header = self.table.horizontalHeaderItem(col).text()
            item = self.table.item(row, col)
            data[header] = item.text() if item else ""
        return data
    
    def on_double_click(self, index):
        """Двойной клик - редактирование"""
        self.on_edit()
    
    def on_add(self):
        """Добавление записи"""
        dialog = EditDialog(self.columns, {}, self)
        if dialog.exec_() == QDialog.Accepted:
            self.insert_data(dialog.get_data())
    
    def on_edit(self):
        """Редактирование записи"""
        row = self.get_selected_row()
        if row is None:
            return
        
        data = self.get_row_data(row)
        dialog = EditDialog(self.columns, data, self)
        if dialog.exec_() == QDialog.Accepted:
            self.update_data(row, dialog.get_data())
    
    def on_delete(self):
        """Удаление записи"""
        row = self.get_selected_row()
        if row is None:
            return
        
        record_id = self.table.item(row, 0).text()
        reply = QMessageBox.question(self, "Подтверждение", 
                                   "Удалить запись?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.delete_data(record_id)
    
    # Методы для переопределения
    def update_data(self, row, data):
        pass
    
    def insert_data(self, data):
        pass
    
    def delete_data(self, record_id):
        pass


class EditDialog(QDialog):
    """Диалог редактирования"""
    
    def __init__(self, columns, data, parent=None):
        super().__init__(parent)
        self.columns = columns
        self.data = data
        self.setWindowTitle("Редактирование записи")
        self.resize(400, 500)
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout()
        layout.setSpacing(15)
        
        self.widgets = {}
        
        for column in self.columns:
            if column.lower() in ['id', '№']:
                continue
            
            value = self.data.get(column, "")
            
            # Определяем тип виджета по названию колонки
            if any(word in column.lower() for word in ['date', 'годности', 'дата']):
                widget = QDateEdit()
                try:
                    if value:
                        # Пробуем распарсить дату
                        if '-' in value:  # формат YYYY-MM-DD
                            parts = value.split('-')
                            if len(parts) == 3:
                                qdate = QDate(int(parts[0]), int(parts[1]), int(parts[2]))
                                widget.setDate(qdate)
                        elif '.' in value:  # формат DD.MM.YYYY
                            parts = value.split('.')
                            if len(parts) == 3:
                                qdate = QDate(int(parts[2]), int(parts[1]), int(parts[0]))
                                widget.setDate(qdate)
                except:
                    widget.setDate(QDate.currentDate().addYears(1))
                widget.setCalendarPopup(True)
                
            elif any(word in column.lower() for word in ['price', 'цена', 'cost']):
                widget = QDoubleSpinBox()
                widget.setRange(0, 999999.99)
                try:
                    val = float(str(value).replace('₽', '').strip())
                    widget.setValue(val)
                except:
                    widget.setValue(0)
                widget.setSuffix(" ₽")
                
            elif any(word in column.lower() for word in ['quantity', 'count', 'количество', 'рейтинг']):
                widget = QSpinBox()
                widget.setRange(0, 999999)
                try:
                    widget.setValue(int(value))
                except:
                    widget.setValue(0)
                
            elif any(word in column.lower() for word in ['reason', 'причина']):
                widget = QComboBox()
                reasons = ['Истек срок годности', 'Брак упаковки', 'Бой', 'Повреждение', 'Другое']
                widget.addItems(reasons)
                if value in reasons:
                    widget.setCurrentText(value)
                    
            else:
                widget = QLineEdit()
                widget.setText(str(value))
            
            layout.addRow(column + ":", widget)
            self.widgets[column] = widget
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def get_data(self):
        """Получить данные из формы"""
        data = {}
        for column, widget in self.widgets.items():
            if isinstance(widget, QDateEdit):
                data[column] = widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, (QDoubleSpinBox, QSpinBox)):
                data[column] = str(widget.value())
            elif isinstance(widget, QComboBox):
                data[column] = widget.currentText()
            else:
                data[column] = widget.text()
        return data