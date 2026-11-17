import json, sqlite3, threading
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).with_name("airline.db")
_lock = threading.Lock()


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def init():
    with _lock:
        c = _conn()
        with c:
            c.executescript("""
            CREATE TABLE IF NOT EXISTS weather(airport TEXT PRIMARY KEY, data TEXT, live INTEGER, ts TEXT);
            CREATE TABLE IF NOT EXISTS weather_history(id INTEGER PRIMARY KEY, airport TEXT, data TEXT, ts TEXT);
            CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, airport TEXT, type TEXT, note TEXT, ts TEXT);
            CREATE TABLE IF NOT EXISTS overrides(airport TEXT PRIMARY KEY, preset TEXT);
            CREATE TABLE IF NOT EXISTS flight_latest(flight TEXT PRIMARY KEY, status TEXT, delay INTEGER);
            CREATE TABLE IF NOT EXISTS flight_changes(id INTEGER PRIMARY KEY, flight TEXT, status TEXT,
                delay INTEGER, score INTEGER, reasons TEXT, ts TEXT);
            """)
        c.close()


def _run(sql, args=(), fetch=False):
    with _lock:
        c = _conn()
        try:
            with c:
                cur = c.execute(sql, args)
                return [dict(r) for r in cur.fetchall()] if fetch else cur.rowcount
        finally:
            c.close()


def save_weather(airport, data, live):
    _run("REPLACE INTO weather VALUES(?,?,?,?)", (airport, json.dumps(data), int(live), now()))
    _run("INSERT INTO weather_history(airport,data,ts) VALUES(?,?,?)", (airport, json.dumps(data), now()))


def get_weather():
    rows = _run("SELECT * FROM weather", fetch=True)
    return {r["airport"]: {**json.loads(r["data"]), "live": bool(r["live"])} for r in rows}


def add_event(airport, type_, note):
    _run("INSERT INTO events(airport,type,note,ts) VALUES(?,?,?,?)", (airport, type_, note, now()))


def get_events():
    return _run("SELECT * FROM events ORDER BY id DESC", fetch=True)


def delete_event(event_id):
    return _run("DELETE FROM events WHERE id=?", (event_id,))


def set_override(airport, preset):
    _run("REPLACE INTO overrides VALUES(?,?)", (airport, preset))


def get_overrides():
    return {r["airport"]: r["preset"] for r in _run("SELECT * FROM overrides", fetch=True)}


def clear_all():
    _run("DELETE FROM events")
    _run("DELETE FROM overrides")


def log_changes(flights):
    """Store a history row whenever a flight's status/delay differs from the last known one."""
    last = {r["flight"]: (r["status"], r["delay"]) for r in _run("SELECT * FROM flight_latest", fetch=True)}
    changed = []
    for f in flights:
        cur = (f["status"], f["delay"])
        prev = last.get(f["no"])
        if prev == cur:
            continue
        if prev is not None or cur != ("On time", 0):
            _run("INSERT INTO flight_changes(flight,status,delay,score,reasons,ts) VALUES(?,?,?,?,?,?)",
                 (f["no"], f["status"], f["delay"], f["score"], "; ".join(f["reasons"]), now()))
            changed.append(f["no"])
        _run("REPLACE INTO flight_latest VALUES(?,?,?)", (f["no"], *cur))
    return changed


def get_changes(limit=50, flight=None):
    q, args = "SELECT * FROM flight_changes", []
    if flight:
        q += " WHERE flight=?"
        args.append(flight)
    q += " ORDER BY id DESC LIMIT ?"
    args.append(limit)
    return _run(q, args, fetch=True)
