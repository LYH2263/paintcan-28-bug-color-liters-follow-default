"""色号批次模块：解析本次测算所用色号，并把色号与当时的测算量一并钉选。"""

DEFAULT_COLOR_BATCH = "PB-2000"


class EmptyColorBatchError(ValueError):
    """整单色号为空或仅空白时拒绝测算。"""


def normalize(code: str | None) -> str:
    """去除首尾空白；空串或 None 归一为空串。"""
    return (code or "").strip()


def resolve(code: str | None, default_code: str | None = None) -> str:
    """显式色号优先；字段缺省(None)时回退默认色号；显式空/空白或无默认可用则拒绝。"""
    if code is not None:
        explicit = normalize(code)
        if not explicit:
            raise EmptyColorBatchError("色号不能为空")
        return explicit
    fallback = normalize(default_code)
    if not fallback:
        raise EmptyColorBatchError("色号不能为空")
    return fallback


def pin(color_batch: str, net_m2: float, liters: float, coverage: float, coats: int) -> dict:
    """把色号与测算当时的净面积、升数、涂布率、遍数钉选为不可漂移的快照。"""
    return {
        "color_batch": color_batch,
        "net_m2": float(net_m2),
        "liters": float(liters),
        "coverage": float(coverage),
        "coats": int(coats),
    }
