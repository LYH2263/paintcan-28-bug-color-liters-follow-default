import json
from app.db import connect
from app.engines.estimate import estimate_room
from app.modules.color_batch import DEFAULT_COLOR_BATCH, pin


def init_db():
    conn = connect()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS rooms(id INTEGER PRIMARY KEY, name TEXT, length REAL, width REAL, height REAL);
    CREATE TABLE IF NOT EXISTS openings(id INTEGER PRIMARY KEY, room_id INTEGER, kind TEXT, w REAL, h REAL);
    CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
    CREATE TABLE IF NOT EXISTS calc_runs(id INTEGER PRIMARY KEY, kind TEXT, room_id INTEGER, input_json TEXT, result_json TEXT, created_at TEXT);
    """)
    # 幂等补齐默认色号：既有库升级后也有缺省值，用户未显式改动时始终存在
    conn.execute("INSERT OR IGNORE INTO settings(key,value) VALUES ('default_color_batch',?)", (DEFAULT_COLOR_BATCH,))
    if conn.execute("SELECT COUNT(*) c FROM rooms").fetchone()["c"] == 0:
        conn.execute("INSERT INTO rooms(name,length,width,height) VALUES ('客厅',5.0,4.0,2.8)")
        conn.execute("INSERT INTO rooms(name,length,width,height) VALUES ('卧室(多种洞)',4.0,3.2,2.8)")
        conn.execute("INSERT INTO openings(room_id,kind,w,h) VALUES (1,'door',0.9,2.1)")
        conn.execute("INSERT INTO openings(room_id,kind,w,h) VALUES (1,'window',1.5,1.4)")
        conn.execute("INSERT INTO openings(room_id,kind,w,h) VALUES (2,'door',0.9,2.1)")
        conn.execute("INSERT INTO openings(room_id,kind,w,h) VALUES (2,'window',1.8,1.5)")
        conn.execute("INSERT INTO openings(room_id,kind,w,h) VALUES (2,'window',1.2,1.5)")
        conn.execute("INSERT INTO settings(key,value) VALUES ('coverage','8')")
        conn.execute("INSERT INTO settings(key,value) VALUES ('coats','2')")
        est = estimate_room(5, 4, 2.8, [{"w": 0.9, "h": 2.1}, {"w": 1.5, "h": 1.4}], 8, 2)
        snapshot = pin(DEFAULT_COLOR_BATCH, est["net_m2"], est["liters"], 8, 2)
        conn.execute("INSERT INTO calc_runs(kind,room_id,input_json,result_json,created_at) VALUES ('estimate',1,?,?,datetime('now'))",
            (json.dumps({"room_id": 1, **snapshot}, ensure_ascii=False), json.dumps(est, ensure_ascii=False)))
        conn.commit()
    conn.close()
