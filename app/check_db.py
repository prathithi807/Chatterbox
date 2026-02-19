from database import get_connection

conn = get_connection()
cur = conn.cursor()

cur.execute("SELECT username, content, timestamp FROM messages")
rows = cur.fetchall()

print("MESSAGES IN DB:")
for row in rows:
    print(row)

conn.close()
