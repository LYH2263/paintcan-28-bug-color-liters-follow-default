import tempfile
import unittest
from pathlib import Path
from unittest import mock

import app.config as config
import app.db as db
from app.modules import color_batch
from app.seed import init_db
from app.services.paint_service import ColorBatchRejected, PaintService


class ColorBatchUnitTests(unittest.TestCase):
    def test_normalize_trims_whitespace(self):
        self.assertEqual(color_batch.normalize("  PB-1 "), "PB-1")
        self.assertEqual(color_batch.normalize(None), "")

    def test_resolve_explicit_wins(self):
        self.assertEqual(color_batch.resolve(" RED-7 ", "PB-2000"), "RED-7")

    def test_resolve_missing_field_falls_back_to_default(self):
        self.assertEqual(color_batch.resolve(None, "PB-2000"), "PB-2000")

    def test_resolve_blank_explicit_is_rejected_even_with_default(self):
        # 显式传入空串/纯空白：整单拒绝，不得悄悄替换为默认色号
        with self.assertRaises(color_batch.EmptyColorBatchError):
            color_batch.resolve("   ", "PB-2000")

    def test_resolve_rejects_empty_pair(self):
        with self.assertRaises(color_batch.EmptyColorBatchError):
            color_batch.resolve(None, " ")

    def test_pin_snapshot_values(self):
        snap = color_batch.pin("RED-7", 46.41, 11.6, 8.0, 2)
        self.assertEqual(snap, {"color_batch": "RED-7", "net_m2": 46.41,
                                "liters": 11.6, "coverage": 8.0, "coats": 2})


class EstimatePinningTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        db_path = Path(self.tmp.name) / "app.db"
        self._patches = [
            mock.patch.object(config, "DATA_DIR", Path(self.tmp.name)),
            mock.patch.object(db, "DB_PATH", db_path),
        ]
        for p in self._patches:
            p.start()
        init_db()

    def tearDown(self):
        for p in self._patches:
            p.stop()
        self.tmp.cleanup()

    def _count_runs(self):
        return db.connect().execute("SELECT COUNT(*) n FROM calc_runs").fetchone()["n"]

    def test_explicit_color_pinned_on_persist(self):
        with PaintService() as s:
            before = self._count_runs()
            r = s.estimate(1, True, color_batch_code="RED-01")
            self.assertEqual(r["color_batch"], "RED-01")
            self.assertEqual(r["liters"], 11.6)
            self.assertEqual(r["net_m2"], 46.41)
            self.assertEqual(r["coverage"], 8.0)
            self.assertEqual(r["coats"], 2)
            self.assertIsNotNone(r["run_id"])
            view = s.run_detail(r["run_id"])
        self.assertEqual(self._count_runs(), before + 1)
        self.assertEqual(view["color_batch"], "RED-01")
        self.assertEqual(view["liters"], 11.6)
        self.assertEqual(view["net_m2"], 46.41)
        self.assertEqual(view["coverage"], 8.0)
        self.assertEqual(view["coats"], 2)

    def test_default_color_used_when_field_absent(self):
        with PaintService() as s:
            r = s.estimate(1, True)
        self.assertEqual(r["color_batch"], color_batch.DEFAULT_COLOR_BATCH)

    def test_blank_color_rejects_and_writes_nothing(self):
        with PaintService() as s:
            before = self._count_runs()
            with self.assertRaises(ColorBatchRejected):
                s.estimate(1, True, color_batch_code="   ")
        self.assertEqual(self._count_runs(), before)

    def test_persist_false_returns_color_but_writes_nothing(self):
        with PaintService() as s:
            before = self._count_runs()
            r = s.estimate(1, False, color_batch_code="TRY-9")
            self.assertIsNone(r["run_id"])
            self.assertEqual(r["color_batch"], "TRY-9")
            self.assertEqual(r["liters"], 11.6)
        self.assertEqual(self._count_runs(), before)

    def test_changing_default_does_not_mutate_old_run(self):
        with PaintService() as s:
            old = s.estimate(1, True, color_batch_code="PB-2000")
            old_id = old["run_id"]
            s.update_default_color_batch("BL-999")
            frozen = s.run_detail(old_id)
            newer = s.estimate(1, True)
            newer_id = newer["run_id"]
            again = s.run_detail(old_id)
            fresh = s.run_detail(newer_id)
        # 旧记录的写入时色号与升数不随默认色号漂移
        self.assertEqual(frozen["color_batch"], "PB-2000")
        self.assertEqual(frozen["liters"], 11.6)
        self.assertEqual(again["color_batch"], "PB-2000")
        self.assertEqual(again["liters"], 11.6)
        # 此后当场再测才用新默认色
        self.assertEqual(newer["color_batch"], "BL-999")
        self.assertEqual(fresh["color_batch"], "BL-999")

    def test_blank_default_rejected(self):
        with PaintService() as s:
            with self.assertRaises(ColorBatchRejected):
                s.update_default_color_batch("  ")


if __name__ == "__main__":
    unittest.main()
