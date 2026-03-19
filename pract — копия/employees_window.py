# employees_window.py
from PyQt5.QtWidgets import QTableWidgetItem
from base_table_window import TableWindow
from PyQt5.QtWidgets import QMessageBox
from db_connection import get_connection

class EmployeesWindow(TableWindow):
    def __init__(self, user):
        columns = ["ID", "ФИО", "Должность", "Телефон", "Дата приема", "Логин"]
        super().__init__("employees", columns, "👥 Управление сотрудниками", user)
    
    def load_data(self):
        """Загрузка сотрудников"""
        conn = get_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT e.id, 
                       e.surname || ' ' || e.name || COALESCE(' ' || e.middle_name, ''),
                       p.title, e.phone, e.hire_date, u.username
                FROM employees e
                JOIN users u ON e.user_id = u.id
                JOIN Post p ON e.idPost = p.idPost
                ORDER BY e.surname;
            """)
            data = cursor.fetchall()
            
            self.table.setRowCount(len(data))
            for row_idx, row in enumerate(data):
                for col_idx, value in enumerate(row):
                    if value is None:
                        item = QTableWidgetItem("")
                    elif col_idx == 4:  # hire_date
                        item = QTableWidgetItem(value.strftime("%d.%m.%Y"))
                    else:
                        item = QTableWidgetItem(str(value))
                    self.table.setItem(row_idx, col_idx, item)
                    
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()