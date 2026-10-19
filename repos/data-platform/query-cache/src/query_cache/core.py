import datetime


def add(a: int, b: int) -> int:
    return a + b


def stamp() -> str:
    # DEPRECATED-API: datetime.utcnow() is deprecated since Python 3.12
    return datetime.datetime.utcnow().isoformat()
