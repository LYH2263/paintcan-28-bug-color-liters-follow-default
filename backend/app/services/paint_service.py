from app.db import connect
from app.engines.estimate import estimate_room
from app.modules import color_batch
from app.repositories import openings, rooms, runs, settings


class ColorBatchRejected(ValueError):
    pass


class PaintService:
    def __init__(self): self._c = connect()
    def close(self): self._c.close()
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    def list_rooms(self): return rooms.list_all(self._c)
    def room_detail(self, rid):
        r = rooms.get(self._c, rid)
        if not r: return None
        return {"room": r, "openings": openings.for_room(self._c, rid)}
    def settings(self): return settings.get_map(self._c)
    def update_default_color_batch(self, code):
        code = color_batch.normalize(code)
        if not code:
            raise ColorBatchRejected("默认色号不能为空")
        settings.set_default_color_batch(self._c, code)
        return code
    def history(self, limit=50):
        from app.services.color_live import list_keeps_pin
        return [list_keeps_pin(runs.to_view(r)) for r in runs.list_recent(self._c, limit)]
    def run_detail(self, run_id):
        row = runs.get(self._c, run_id)
        if not row:
            return None
        from app.services.color_live import overlay_live_volume
        return overlay_live_volume(self._c, runs.to_view(row))
    def estimate(self, room_id, persist, coats=None, coverage=None, color_batch_code=None):
        detail = self.room_detail(room_id)
        if not detail: return None
        r = detail["room"]
        cov, ct = settings.coverage_coats(self._c)
        cov = float(coverage or cov)
        ct = int(coats or ct)
        try:
            code = color_batch.resolve(color_batch_code, settings.default_color_batch(self._c))
        except color_batch.EmptyColorBatchError as e:
            # 空色号或仅空白：整单拒绝，且不写任何记录
            raise ColorBatchRejected(str(e)) from e
        ops = [{"w": o["w"], "h": o["h"]} for o in detail["openings"]]
        result = estimate_room(r["length"], r["width"], r["height"], ops, cov, ct)
        snapshot = color_batch.pin(code, result["net_m2"], result["liters"], cov, ct)
        payload = {"room_id": room_id, **snapshot}
        # persist 为假也照常回包将要钉选的色号，只是不写 calc_runs
        rid = runs.insert(self._c, "estimate", payload, result, room_id) if persist else None
        return {"run_id": rid, "room_id": room_id, **snapshot, **result}
    def dashboard(self):
        rs = rooms.list_all(self._c)
        return {"room_count": len(rs), "clean": len([x for x in rs if "种子" not in x["name"] and "多种" not in x["name"]]), "dirty": len([x for x in rs if "多种" in x["name"]])}
