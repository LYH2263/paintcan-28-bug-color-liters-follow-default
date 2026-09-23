import json
from datetime import datetime, timezone


def insert(conn, kind, payload, result, room_id=None):
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute("INSERT INTO calc_runs(kind,room_id,input_json,result_json,created_at) VALUES (?,?,?,?,?)",
        (kind, room_id, json.dumps(payload, ensure_ascii=False), json.dumps(result, ensure_ascii=False), now))
    conn.commit(); return int(cur.lastrowid)


def get(conn, run_id: int):
    row = conn.execute("SELECT * FROM calc_runs WHERE id=?", (run_id,)).fetchone()
    return dict(row) if row else None


def list_recent(conn, limit=50):
    return [dict(r) for r in conn.execute("SELECT * FROM calc_runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]


def to_view(row: dict) -> dict:
    """展开一条测算记录：写入时钉选的色号与升数随记录返回，不随后续设置漂移。

    色号优先取 input_json 钉选快照；早期无该字段的记录回退 result_json。
    """
    try:
        inp = json.loads(row.get("input_json") or "{}")
    except json.JSONDecodeError:
        inp = {}
    try:
        res = json.loads(row.get("result_json") or "{}")
    except json.JSONDecodeError:
        res = {}
    return {
        "id": row["id"],
        "kind": row.get("kind"),
        "room_id": row.get("room_id"),
        "created_at": row.get("created_at"),
        "color_batch": inp.get("color_batch") or res.get("color_batch"),
        "liters": inp.get("liters", res.get("liters")),
        "net_m2": inp.get("net_m2", res.get("net_m2")),
        "coverage": inp.get("coverage", res.get("coverage")),
        "coats": inp.get("coats", res.get("coats")),
        "input": inp,
        "result": res,
    }


def detail_volume_hint(row: dict) -> dict:
    """Hint fields for UI that prefers live-looking coverage labels."""
    view = to_view(row)
    return {
        "color_batch": view.get("color_batch"),
        "net_m2": view.get("net_m2"),
        "pinned_liters": view.get("liters"),
    }
