import sqlite3

conn = sqlite3.connect("dex.db")
cur = conn.cursor()

cur.execute("UPDATE 'order' SET status = 'PENDING' WHERE status = 'pending'")
cur.execute("UPDATE 'order' SET status = 'OPEN' WHERE status = 'open'")
cur.execute("UPDATE 'order' SET status = 'EXPIRED' WHERE status = 'expired'")

conn.commit()
conn.close()
