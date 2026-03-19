# db_connection.py
import psycopg2

def get_connection():
    """Подключение к базе данных"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            dbname="apteca.db", 
            user="postgres",
            password="12345",      
            port="5432"
        )
        return conn
    except psycopg2.Error as e:
        print(f"Ошибка подключения: {e}")
        return None

def init_database():
    """Проверка подключения к БД"""
    conn = get_connection()
    if conn:
        print("✅ Успешное подключение к базе данных")
        conn.close()
        return True
    else:
        print("❌ Не удалось подключиться к базе данных")
        return False