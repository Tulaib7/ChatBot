import psycopg2
from bytez import Bytez

key = "bbaa8bcf547a6aa15aed3656655eb814"
sdk = Bytez(key)
model = sdk.model("openai/gpt-5")

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="mydb",
        user="postgres",
        password="hypervanoM20",
        port=5432
    )

def extract_schema():
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public';
        """)
        tables = [t[0] for t in cur.fetchall()]

        schema = {}

        for table in tables:
            cur.execute(f"""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = '{table}';
            """)
            cols = [c[0] for c in cur.fetchall()]
            schema[table] = cols

        conn.close()
        return schema

    except Exception as e:
        return {}

def run_sql(query):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query)

        if query.strip().upper().startswith("SELECT"):
            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
            conn.close()
            return [dict(zip(colnames, row)) for row in rows]

        conn.commit()
        conn.close()
        return "OK"
    except Exception as e:
        return f"SQL Error: {str(e)}"

def main():
    messages = []
    print("Chatbot connected. Type exit to quit.")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("Bot: Bye")
            break

        messages.append({"role": "user", "content": user_input})

        schema = extract_schema()
        schema_text = ""

        for table, cols in schema.items():
            schema_text += f"{table}: {', '.join(cols)}. "

        system_prompt = (
            "You translate natural language into SQL. "
            "Use PostgreSQL syntax. "
            "Here is the available database schema: "
            f"{schema_text} "
            "When the user asks about data, respond with SQL only."
            "If user asks something outside database. Stricly respond with a 'No Information Found'"
        )

        full_msg = [{"role": "system", "content": system_prompt}] + messages
        response = model.run(full_msg)
        reply = response.output["content"]

        sql_ops = ["SELECT", "INSERT", "UPDATE", "DELETE"]

        if any(op in reply.upper() for op in sql_ops):
            print("Bot: Running SQL...")
            result = run_sql(reply)
            print("Bot:", result)
        else:
            print("Bot:", reply)

        messages.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    main()
