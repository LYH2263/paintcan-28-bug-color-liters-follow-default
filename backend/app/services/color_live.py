"""Recompute liters from current wall coverage while keeping color_batch label."""
import json
from app.engines.paint_volume import paint_liters
from app.repositories import settings


def _parse(raw):
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw or "{}")
    except (TypeError, ValueError, json.JSONDecodeError):
        return {}


def current_coverage_coats(conn):
    cov, coats = settings.coverage_coats(conn)
    return float(cov), int(coats)


def live_liters_for_net(conn, net_m2):
    cov, coats = current_coverage_coats(conn)
    vol = paint_liters(float(net_m2), cov, coats)
    return {
        "liters": vol["liters"],
        "coverage": vol["coverage"],
        "coats": vol["coats"],
        "net_m2": float(net_m2),
    }


def overlay_live_volume(conn, view: dict) -> dict:
    """Preserve color_batch from pin; replace liters/coverage/coats with live defaults."""
    out = dict(view)
    inp = out.get("input") or {}
    res = out.get("result") or {}
    net = out.get("net_m2")
    if net is None:
        net = inp.get("net_m2", res.get("net_m2"))
    if net is None:
        return out
    live = live_liters_for_net(conn, net)
    label = out.get("color_batch") or inp.get("color_batch") or res.get("color_batch")
    out["color_batch"] = label
    out["liters"] = live["liters"]
    out["coverage"] = live["coverage"]
    out["coats"] = live["coats"]
    out["net_m2"] = live["net_m2"]
    # keep nested result liters in sync so detail panels that read result also drift
    if isinstance(out.get("result"), dict):
        merged = dict(out["result"])
        merged["liters"] = live["liters"]
        merged["coverage"] = live["coverage"]
        merged["coats"] = live["coats"]
        out["result"] = merged
    return out


def list_keeps_pin(view: dict) -> dict:
    """History list path: return view unchanged (pinned liters)."""
    return view
