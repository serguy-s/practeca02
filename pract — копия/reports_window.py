# reports_window.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from db_connection import get_connection
from datetime import datetime
from word_exporter import save_to_word

class ReportsWindow(QWidget):
    def __init__(self, user, can_export=False):
        super().__init__()
        self.user = user
        self.can_export = can_export
        self.setWindowTitle(f"📊 Отчеты {'и экспорт' if can_export else ''}")
        self.resize(800, 600)
        self.data = {}
        self.totals = {}
        self.init_ui()
        self.update_previews()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"📊 Отчеты {self.user['surname']}", alignment=Qt.AlignCenter))
        
        tabs = QTabWidget()
        reports = [
            ("❌ Просрочка", "#e74c3c", "expired"),
            ("📝 Списания", "#f39c12", "writeoffs"), 
            ("📦 Остатки", "#3498db", "stock")
        ]
        
        for name, color, func in reports:
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            
            btn = QPushButton(f"📋 Сформировать отчет")
            btn.setStyleSheet(f"background-color: {color}; color: white; padding: 15px; font-weight: bold;")
            btn.clicked.connect(lambda checked, f=func: self.generate_report(f))
            tab_layout.addWidget(btn)
            
            preview = QTextEdit()
            preview.setMaximumHeight(150)
            preview.setReadOnly(True)
            setattr(self, f"{func}_preview", preview)
            tab_layout.addWidget(preview)
            
            if self.can_export:
                export_btn = QPushButton("💾 Экспорт в Word")
                export_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px;")
                export_btn.clicked.connect(lambda checked, f=func: self.export_report(f))
                tab_layout.addWidget(export_btn)
            
            tabs.addTab(tab, name)
        
        layout.addWidget(tabs)
        
        if not self.can_export:
            layout.addWidget(QLabel("⚠️ Экспорт только для заведующего", alignment=Qt.AlignCenter))
        
        self.setLayout(layout)
    
    def update_previews(self):
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()
        try:
            # Просрочка
            cursor.execute("SELECT COUNT(*), SUM(Quantity), SUM(Quantity*Price) FROM Product WHERE Expiration_date < CURRENT_DATE")
            exp = cursor.fetchone()
            self.expired_preview.setText(f"Просрочено: {exp[0] or 0}\nКол-во: {exp[1] or 0} шт.\nСумма: {exp[2] or 0:.2f} ₽")
            
            # Списания за 30 дней
            cursor.execute("SELECT COUNT(*), SUM(Quantity) FROM Write_downs WHERE Date >= CURRENT_DATE - INTERVAL '30 days'")
            wr = cursor.fetchone()
            self.writeoffs_preview.setText(f"Списаний: {wr[0] or 0}\nВсего: {wr[1] or 0} шт.")
            
            # Остатки
            cursor.execute("SELECT COUNT(*), SUM(Quantity), SUM(Quantity*Price) FROM Product")
            st = cursor.fetchone()
            self.stock_preview.setText(f"Позиций: {st[0] or 0}\nКол-во: {st[1] or 0} шт.\nСумма: {st[2] or 0:.2f} ₽")
        finally:
            cursor.close()
            conn.close()
    
    def generate_report(self, report_type):
        conn = get_connection()
        if not conn: return
        cursor = conn.cursor()
        try:
            if report_type == 'expired':
                cursor.execute("SELECT Title, Manufacturer, Expiration_date, Quantity, Price FROM Product WHERE Expiration_date < CURRENT_DATE")
                data = cursor.fetchall()
                title = "ОТЧЕТ ПО ПРОСРОЧЕННЫМ ТОВАРАМ"
                
                # Считаем итоги
                total_qty = sum(row[3] for row in data)
                total_sum = sum(row[3] * row[4] for row in data)
                
                # Формируем отчет
                text = f"{title}\n"
                text += "="*100 + "\n"
                text += f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
                text += f"Сотрудник: {self.user['surname']} {self.user['name']}\n"
                text += "="*100 + "\n\n"
                
                # Заголовки таблицы для просрочки
                text += f"{'№':<4} {'Наименование':<35} {'Производитель':<20} {'Срок годности':<15} {'Кол-во':<8} {'Цена':<10} {'Сумма':<10}\n"
                text += "-"*102 + "\n"
                
                for i, row in enumerate(data, 1):
                    summa = row[3] * row[4]
                    text += f"{i:<4} {row[0][:33]:<35} {row[1][:18]:<20} "
                    text += f"{row[2].strftime('%d.%m.%Y'):<15} {row[3]:<8} {row[4]:<10.2f} {summa:<10.2f}\n"
                
            elif report_type == 'writeoffs':
                cursor.execute("""
                    SELECT p.Title, w.Quantity, w.Date, w.Reason, u.surname || ' ' || u.name as user_name
                    FROM Write_downs w 
                    JOIN Product p ON w.IDProduct = p.idProduct 
                    JOIN "user" u ON w.IDUser = u.idUser
                    ORDER BY w.Date DESC
                """)
                data = cursor.fetchall()
                title = "ОТЧЕТ ПО СПИСАНИЯМ"
                
                # Считаем итоги
                total_qty = sum(row[1] for row in data)
                
                # Формируем отчет
                text = f"{title}\n"
                text += "="*100 + "\n"
                text += f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
                text += f"Сотрудник: {self.user['surname']} {self.user['name']}\n"
                text += "="*100 + "\n\n"
                
                # Заголовки таблицы для списаний
                text += f"{'№':<4} {'Наименование':<35} {'Кол-во':<8} {'Дата списания':<15} {'Причина':<25} {'Кто списал':<20}\n"
                text += "-"*107 + "\n"
                
                for i, row in enumerate(data, 1):
                    text += f"{i:<4} {row[0][:33]:<35} {row[1]:<8} "
                    text += f"{row[2].strftime('%d.%m.%Y'):<15} {row[3][:23]:<25} {row[4][:18]:<20}\n"
                
            else:  # stock
                cursor.execute("SELECT Title, Manufacturer, Quantity, Price, Expiration_date FROM Product ORDER BY Title")
                data = cursor.fetchall()
                title = "ОТЧЕТ ПО ОСТАТКАМ ТОВАРОВ"
                
                # Считаем итоги
                total_qty = sum(row[2] for row in data)
                total_sum = sum(row[2] * row[3] for row in data)
                
                # Формируем отчет
                text = f"{title}\n"
                text += "="*100 + "\n"
                text += f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
                text += f"Сотрудник: {self.user['surname']} {self.user['name']}\n"
                text += "="*100 + "\n\n"
                
                # Заголовки таблицы для остатков
                text += f"{'№':<4} {'Наименование':<35} {'Производитель':<20} {'Кол-во':<8} {'Цена':<10} {'Срок годности':<15}\n"
                text += "-"*92 + "\n"
                
                for i, row in enumerate(data, 1):
                    date_str = row[4].strftime('%d.%m.%Y') if row[4] else 'н/д'
                    text += f"{i:<4} {row[0][:33]:<35} {row[1][:18]:<20} {row[2]:<8} {row[3]:<10.2f} {date_str:<15}\n"
            
            self.data[report_type] = data
            
            if not data:
                QMessageBox.information(self, "Инфо", "Нет данных")
                return
            
            # ИТОГИ ПОСЛЕ ТАБЛИЦЫ
            text += "\n" + "="*100 + "\n"
            text += "ИТОГИ:\n"
            text += f"Количество позиций: {len(data)}\n"
            text += f"Общее количество: {total_qty} шт.\n"
            if report_type != 'writeoffs':
                text += f"Общая сумма: {total_sum:.2f} ₽\n"
            
            self.totals[report_type] = (len(data), total_qty, total_sum if report_type != 'writeoffs' else 0)
            
            # Показываем отчет
            dialog = QDialog(self)
            dialog.setWindowTitle(title)
            dialog.resize(1100, 600)
            
            dlg_layout = QVBoxLayout(dialog)
            
            text_edit = QTextEdit()
            text_edit.setPlainText(text)
            text_edit.setFontFamily("Courier New")
            text_edit.setReadOnly(True)
            dlg_layout.addWidget(text_edit)
            
            btn_close = QPushButton("Закрыть")
            btn_close.clicked.connect(dialog.accept)
            dlg_layout.addWidget(btn_close)
            
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            cursor.close()
            conn.close()
    
    def export_report(self, report_type):
        if report_type not in self.data or not self.data[report_type]:
            QMessageBox.warning(self, "Ошибка", "Сначала сформируйте отчет")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить отчет", 
            f"{report_type}_{datetime.now().strftime('%Y%m%d_%H%M')}.docx", 
            "Word (*.docx)"
        )
        
        if filename:
            export_data = list(self.data[report_type])
            
            # Добавляем строку с итогами в конец данных для экспорта
            if report_type in self.totals:
                totals = self.totals[report_type]
                if report_type == 'writeoffs':
                    export_data.append([f"ИТОГО: {totals[0]} позиций", f"{totals[1]} шт."])
                else:
                    export_data.append([f"ИТОГО: {totals[0]} позиций", f"{totals[1]} шт.", f"{totals[2]:.2f} ₽"])
            
            save_to_word(export_data, f"Отчет по {report_type}", filename)
            QMessageBox.information(self, "Успех", f"Отчет сохранен в {filename}")