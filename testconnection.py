import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="mydb",
        user="postgres",
        password="your_password",
        port=5432
    )
    print("Connected")
except Exception as e:
    print("Error:", e)
