# test_report.py
import unittest
import sys
import os
from datetime import date, timedelta
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from db_connection import get_connection

class TestPharmacySystem(unittest.TestCase):
    """Комплексное тестирование аптечной системы"""
    
    @classmethod
    def setUpClass(cls):
        """Подготовка перед всеми тестами"""
        print("\n" + "="*60)
        print("НАЧАЛО ТЕСТИРОВАНИЯ АПТЕЧНОЙ СИСТЕМЫ")
        print("="*60)
        cls.test_products = []
        cls.test_users = []
    
    @classmethod
    def tearDownClass(cls):
        """Очистка после всех тестов"""
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            # Очистка тестовых данных
            for pid in cls.test_products:
                try:
                    cursor.execute("DELETE FROM Product WHERE idProduct = %s;", (pid,))
                except:
                    pass
            for uid in cls.test_users:
                try:
                    cursor.execute('DELETE FROM "user" WHERE idUser = %s;', (uid,))
                except:
                    pass
            conn.commit()
            cursor.close()
            conn.close()
        
        print("\n" + "="*60)
        print("ИТОГИ ТЕСТИРОВАНИЯ")
        print("="*60)
    
    # ========== ТЕСТЫ ПОДКЛЮЧЕНИЯ К БД ==========
    def test_1_connection(self):
        """[БД] Проверка подключения к базе данных"""
        conn = get_connection()
        self.assertIsNotNone(conn, "❌ Не удалось подключиться к БД")
        if conn:
            conn.close()
            print("  ✅ Подключение к БД успешно")
    
    def test_2_tables_exist(self):
        """[БД] Проверка существования таблиц"""
        conn = get_connection()
        self.assertIsNotNone(conn)
        cursor = conn.cursor()
        
        tables = ['user', 'Product', 'Write_downs', 'Post']
        for table in tables:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """, (table.lower(),))
            exists = cursor.fetchone()[0]
            self.assertTrue(exists, f"❌ Таблица '{table}' не найдена")
            print(f"  ✅ Таблица '{table}' существует")
        
        cursor.close()
        conn.close()
    
    # ========== ТЕСТЫ ТАБЛИЦЫ user ==========
    def test_3_create_user(self):
        """[user] Создание пользователя"""
        conn = get_connection()
        self.assertIsNotNone(conn)
        cursor = conn.cursor()
        
        # Проверяем наличие должности
        cursor.execute("SELECT idPost FROM Post WHERE idPost = 1;")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO Post (idPost, title) VALUES (1, 'Фармацевт') ON CONFLICT DO NOTHING;")
            conn.commit()
        
        # Создаем пользователя
        cursor.execute('''
            INSERT INTO "user" (login, password, surname, name, idPost)
            VALUES (%s, %s, %s, %s, %s) RETURNING idUser;
        ''', ('testuser', 'testpass', 'Тестов', 'Тест', 1))
        user_id = cursor.fetchone()[0]
        conn.commit()
        self.__class__.test_users.append(user_id)
        
        self.assertIsNotNone(user_id)
        print(f"  ✅ Пользователь создан (ID: {user_id})")
        cursor.close()
        conn.close()
    
    def test_4_read_user(self):
        """[user] Чтение данных пользователя"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT login, surname, name FROM "user" WHERE login = %s;', ('testuser',))
        user = cursor.fetchone()
        
        self.assertIsNotNone(user)
        self.assertEqual(user[0], 'testuser')
        self.assertEqual(user[1], 'Тестов')
        print(f"  ✅ Данные пользователя прочитаны: {user[0]} {user[1]} {user[2]}")
        
        cursor.close()
        conn.close()
    
    def test_5_update_user(self):
        """[user] Обновление данных пользователя"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE "user" SET name = %s WHERE login = %s;', ('Обновлен', 'testuser'))
        conn.commit()
        
        cursor.execute('SELECT name FROM "user" WHERE login = %s;', ('testuser',))
        name = cursor.fetchone()[0]
        
        self.assertEqual(name, 'Обновлен')
        print(f"  ✅ Пользователь обновлен: имя изменено на '{name}'")
        
        cursor.close()
        conn.close()
    
    def test_6_check_password(self):
        """[user] Проверка пароля"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT password FROM "user" WHERE login = %s;', ('testuser',))
        password = cursor.fetchone()[0]
        
        self.assertEqual(password, 'testpass')
        self.assertNotEqual(password, 'wrongpass')
        print(f"  ✅ Пароль пользователя корректен")
        
        cursor.close()
        conn.close()
    
    # ========== ТЕСТЫ ТАБЛИЦЫ Product ==========
    def test_7_create_product(self):
        """[Product] Создание товара"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO Product (Title, Manufacturer, Expiration_date, Quantity, Price)
            VALUES (%s, %s, %s, %s, %s) RETURNING idProduct;
        """, ('Тестовый препарат', 'ТестПроизводитель', date.today() + timedelta(days=365), 100, 99.99))
        product_id = cursor.fetchone()[0]
        conn.commit()
        self.__class__.test_products.append(product_id)
        
        self.assertIsNotNone(product_id)
        print(f"  ✅ Товар создан (ID: {product_id})")
        cursor.close()
        conn.close()
    
    def test_8_read_product(self):
        """[Product] Чтение данных товара"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Берем последний созданный товар
        product_id = self.__class__.test_products[-1] if self.__class__.test_products else None
        self.assertIsNotNone(product_id)
        
        cursor.execute("SELECT Title, Manufacturer, Quantity, Price FROM Product WHERE idProduct = %s;", (product_id,))
        product = cursor.fetchone()
        
        self.assertIsNotNone(product)
        self.assertEqual(product[0], 'Тестовый препарат')
        self.assertEqual(product[2], 100)
        print(f"  ✅ Товар прочитан: {product[0]} ({product[2]} шт.)")
        
        cursor.close()
        conn.close()
    
    def test_9_update_product(self):
        """[Product] Обновление товара"""
        conn = get_connection()
        cursor = conn.cursor()
        
        product_id = self.__class__.test_products[-1] if self.__class__.test_products else None
        self.assertIsNotNone(product_id)
        
        cursor.execute("""
            UPDATE Product SET Quantity = %s, Price = %s WHERE idProduct = %s;
        """, (150, 199.99, product_id))
        conn.commit()
        
        cursor.execute("SELECT Quantity, Price FROM Product WHERE idProduct = %s;", (product_id,))
        updated = cursor.fetchone()
        
        self.assertEqual(updated[0], 150)
        self.assertEqual(float(updated[1]), 199.99)
        print(f"  ✅ Товар обновлен: количество={updated[0]}, цена={updated[1]}")
        
        cursor.close()
        conn.close()
    
    def test_10_expired_product(self):
        """[Product] Поиск просроченных товаров"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Создаем просроченный товар
        cursor.execute("""
            INSERT INTO Product (Title, Manufacturer, Expiration_date, Quantity, Price)
            VALUES (%s, %s, %s, %s, %s) RETURNING idProduct;
        """, ('Просрочка тест', 'Тест', date.today() - timedelta(days=10), 5, 100.00))
        expired_id = cursor.fetchone()[0]
        conn.commit()
        self.__class__.test_products.append(expired_id)
        
        # Ищем просроченные
        cursor.execute("SELECT COUNT(*) FROM Product WHERE Expiration_date < CURRENT_DATE;")
        count = cursor.fetchone()[0]
        
        self.assertGreaterEqual(count, 1)
        print(f"  ✅ Найдено просроченных товаров: {count}")
        
        cursor.close()
        conn.close()
    
    def test_11_expiring_soon(self):
        """[Product] Поиск истекающих товаров"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Создаем истекающий товар
        cursor.execute("""
            INSERT INTO Product (Title, Manufacturer, Expiration_date, Quantity, Price)
            VALUES (%s, %s, %s, %s, %s) RETURNING idProduct;
        """, ('Истекает тест', 'Тест', date.today() + timedelta(days=5), 10, 200.00))
        expiring_id = cursor.fetchone()[0]
        conn.commit()
        self.__class__.test_products.append(expiring_id)
        
        # Ищем истекающие (30 дней)
        cursor.execute("""
            SELECT COUNT(*) FROM Product 
            WHERE Expiration_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days';
        """)
        count = cursor.fetchone()[0]
        
        self.assertGreaterEqual(count, 1)
        print(f"  ✅ Найдено истекающих товаров: {count}")
        
        cursor.close()
        conn.close()
    
    def test_12_stock_total(self):
        """[Product] Подсчет остатков"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*), SUM(Quantity), SUM(Quantity * Price) FROM Product;")
        stats = cursor.fetchone()
        
        print(f"  📊 Статистика товаров:")
        print(f"     - Всего позиций: {stats[0]}")
        print(f"     - Общее количество: {stats[1] or 0} шт.")
        print(f"     - Общая сумма: {stats[2] or 0:.2f} ₽")
        
        cursor.close()
        conn.close()
    
    def test_13_delete_product(self):
        """[Product] Удаление товара"""
        conn = get_connection()
        cursor = conn.cursor()
        
        product_id = self.__class__.test_products.pop() if self.__class__.test_products else None
        self.assertIsNotNone(product_id)
        
        cursor.execute("DELETE FROM Product WHERE idProduct = %s;", (product_id,))
        conn.commit()
        
        cursor.execute("SELECT * FROM Product WHERE idProduct = %s;", (product_id,))
        product = cursor.fetchone()
        
        self.assertIsNone(product)
        print(f"  ✅ Товар ID {product_id} удален")
        
        cursor.close()
        conn.close()

if __name__ == '__main__':
    # Запуск с подробным выводом
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPharmacySystem)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Итоговый отчет
    print("\n" + "="*60)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("="*60)
    print(f"Всего тестов: {result.testsRun}")
    print(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Ошибки: {len(result.errors)}")
    print(f"Падения: {len(result.failures)}")
    
    if result.wasSuccessful():
        print("\n✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print("\n❌ ТЕСТЫ ЗАВЕРШИЛИСЬ С ОШИБКАМИ")
    print("="*60)