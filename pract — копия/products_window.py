# products_window.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QBrush
from db_connection import get_connection
from datetime import date
from base_table_window import TableWindow, EditDialog

class ProductsWindow(TableWindow):
    def __init__(self, user, full_access=True):
        self.full_access = full_access
        columns = ["ID", "Название", "Производитель", "Срок годности", 
                   "Количество", "Цена", "Статус"]
        super().__init__("Product", columns, "💊 Управление товарами", user)
    
    def load_data(self):
        """Загрузка данных"""
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к БД")
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT idProduct, Title, Manufacturer, Expiration_date, Quantity, Price 
                FROM Product ORDER BY Expiration_date;
            """)
            data = cursor.fetchall()
            
            self.table.setRowCount(len(data))
            today = date.today()
            
            for row_idx, row in enumerate(data):
                # ID
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(row[0])))
                # Название
                self.table.setItem(row_idx, 1, QTableWidgetItem(row[1] or ""))
                # Производитель
                self.table.setItem(row_idx, 2, QTableWidgetItem(row[2] or ""))
                # Срок годности
                if row[3]:
                    self.table.setItem(row_idx, 3, QTableWidgetItem(row[3].strftime("%d.%m.%Y")))
                    days_left = (row[3] - today).days
                else:
                    self.table.setItem(row_idx, 3, QTableWidgetItem(""))
                    days_left = 999
                # Количество
                self.table.setItem(row_idx, 4, QTableWidgetItem(str(row[4] or 0)))
                # Цена
                self.table.setItem(row_idx, 5, QTableWidgetItem(f"{float(row[5]):.2f} ₽" if row[5] else "0.00 ₽"))
                
                # Статус
                if days_left < 0:
                    status = "❌ ПРОСРОЧЕН"
                    color = QColor("#e74c3c")
                elif days_left <= 10:
                    status = f"⚠️ Критично! {days_left} дн."
                    color = QColor("#e67e22")
                elif days_left <= 30:
                    status = f"⚠️ Скоро {days_left} дн."
                    color = QColor("#f39c12")
                else:
                    status = f"✅ Годен"
                    color = QColor("#27ae60")
                
                status_item = QTableWidgetItem(status)
                status_item.setForeground(QBrush(color))
                self.table.setItem(row_idx, 6, status_item)
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    def insert_data(self, data):
        """Добавление товара"""
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Product (Title, Manufacturer, Expiration_date, Quantity, Price)
                VALUES (%s, %s, %s, %s, %s);
            """, (
                data['Название'],
                data.get('Производитель', ''),
                data['Срок годности'],
                int(data['Количество']),
                float(data['Цена'])
            ))
            conn.commit()
            self.load_data()  # Обновляем таблицу
            QMessageBox.information(self, "Успех", "Товар добавлен!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    def update_data(self, row, data):
        """Обновление товара"""
        record_id = self.table.item(row, 0).text()
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE Product SET 
                    Title=%s, Manufacturer=%s, Expiration_date=%s,
                    Quantity=%s, Price=%s
                WHERE idProduct=%s;
            """, (
                data['Название'],
                data.get('Производитель', ''),
                data['Срок годности'],
                int(data['Количество']),
                float(data['Цена']),
                record_id
            ))
            conn.commit()
            self.load_data()  # Обновляем таблицу
            QMessageBox.information(self, "Успех", "Данные обновлены!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка обновления:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    def delete_data(self, record_id):
        """Удаление товара"""
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            # Проверяем списания
            cursor.execute("SELECT COUNT(*) FROM Write_downs WHERE IDProduct=%s;", (record_id,))
            if cursor.fetchone()[0] > 0:
                cursor.execute("DELETE FROM Write_downs WHERE IDProduct=%s;", (record_id,))
            
            cursor.execute("DELETE FROM Product WHERE idProduct=%s;", (record_id,))
            conn.commit()
            self.load_data()  # Обновляем таблицу
            QMessageBox.information(self, "Успех", "Товар удален!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка удаления:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()