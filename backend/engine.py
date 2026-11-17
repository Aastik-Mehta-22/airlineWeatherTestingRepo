"""Rules engine: weather + events -> airport risk -> flight status."""
from data import EVENT_TYPES, FLIGHTS, AIRPORTS, CALM


def weather_risk(w: dict):
    score, why = 0, []
    gust = w.get("gust") or 0
    if gust >= 90:
        score += 70; why.append(f"gusts {int(gust)} km/h")
    elif gust >= 60:
        score += 35; why.append(f"gusts {int(gust)} km/h")
    if w.get("code") in (95, 96, 99):
        score += 75; why.append("thunderstorm")
    snow = w.get("snow") or 0
    if snow >= 1 or w.get("code") in (73, 75, 77, 85, 86):
        score += min(70, 30 + snow * 15); why.append("snow")
    vis = w.get("vis") if w.get("vis") is not None else 10000
    if vis < 1000:
        score += 60; why.append(f"visibility {int(vis)} m")
    elif vis < 3000 or w.get("code") in (45, 48):
        score += 30; why.append("low visibility")
    if (w.get("precip") or 0) >= 5:
        score += 25; why.append(f"heavy rain {w['precip']} mm")
    temp = w.get("temp") if w.get("temp") is not None else 20
    if temp <= -15:
        score += 25; why.append(f"extreme cold {temp}C")
    if temp >= 45:
        score += 20; why.append(f"extreme heat {temp}C")
    return min(100, int(score)), why


def event_risk(events):
    score, why = 0, []
    for e in events:
        sev = EVENT_TYPES[e["type"]]["sev"]
        score = max(score, sev) + (10 if score else 0)
        why.append(EVENT_TYPES[e["type"]]["label"].lower())
    return min(100, score), why


def airport_risk(weather: dict, events: list) -> dict:
    ws, ww = weather_risk(weather)
    es, ew = event_risk(events)
    score = min(100, max(ws, es) + min(ws, es) * 0.4)
    return {"score": round(score), "why": ww + ew, "weather": weather}


def flight_impact(f: dict, risks: dict) -> dict:
    o, d = risks[f["frm"]], risks[f["to"]]
    score = max(o["score"], d["score"] * 0.9)
    reasons = [f"{f['frm']}: {r}" for r in o["why"]] + [f"{f['to']}: {r}" for r in d["why"]]
    status, delay = "On time", 0
    if score >= 85:
        status = "Cancelled"
    elif score >= 20:
        status, delay = "Delayed", int(round(score * 2.2 / 5) * 5)
    return {**f, "score": round(score), "status": status, "delay": delay, "reasons": reasons}


def compute(weather: dict, overrides: dict, events: list) -> dict:
    """weather: {code: dict}; overrides: {code: dict}; events: list of event rows."""
    risks = {}
    for code in AIRPORTS:
        w = {**CALM, **weather.get(code, {})}
        w.update(overrides.get(code, {}))
        risks[code] = airport_risk(w, [e for e in events if e["airport"] == code])
    flights = [flight_impact(f, risks) for f in FLIGHTS]
    delayed = [f["delay"] for f in flights if f["delay"]]
    kpis = {
        "flights": len(flights),
        "on_time": sum(f["status"] == "On time" for f in flights),
        "delayed": sum(f["status"] == "Delayed" for f in flights),
        "cancelled": sum(f["status"] == "Cancelled" for f in flights),
        "avg_delay": round(sum(delayed) / len(delayed)) if delayed else 0,
        "active_events": len(events),
    }
    return {"airports": risks, "flights": flights, "kpis": kpis}
