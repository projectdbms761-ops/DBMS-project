import sqlite3
p='dev_fallback.db'
try:
    c=sqlite3.connect(p)
    cur=c.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print('tables:',cur.fetchall())
    for t in ['Room','Student','Allocation','Warden','Hostel']:
        try:
            cur.execute(f"SELECT * FROM {t} LIMIT 5")
            print('#',t,cur.fetchall())
        except Exception as e:
            print('err',t,e)
    c.close()
except Exception as e:
    print('connect error',e)
