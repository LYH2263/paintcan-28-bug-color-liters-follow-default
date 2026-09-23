import sqlite3


def get_map(conn): return {r["key"]: r["value"] for r in conn.execute("SELECT * FROM settings").fetchall()}


def coverage_coats(conn):
    m = get_map(conn)
    return float(m.get("coverage", "8")), int(m.get("coats", "2"))


def default_color_batch(conn) -> str:
    return (get_map(conn).get("default_color_batch") or "").strip()


def set_default_color_batch(conn, code: str):
    conn.execute(
        "INSERT INTO settings(key,value) VALUES ('default_color_batch',?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (code.strip(),),
    )
    conn.commit()
