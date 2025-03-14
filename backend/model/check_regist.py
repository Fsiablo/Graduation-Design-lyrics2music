import sys
sys.path.append(r"D:\study\Graduation-Design\backend\Login")
from templates.config import conn

cur = conn.cursor()

def add_user(username, password):
    # sql commands
    sql = "INSERT INTO user(username, password) VALUES ('%s','%s')" %(username, password)
    conn.ping(reconnect=True)

    # execute(sql)
    cur.execute(sql)
    # commit
    conn.commit()  # 对数据库内容有改变，需要commit()
    conn.close()
