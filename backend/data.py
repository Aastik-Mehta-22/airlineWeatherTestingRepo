AIRPORTS = {
    "DEL": {"name": "Delhi", "lat": 28.56, "lon": 77.10},
    "BOM": {"name": "Mumbai", "lat": 19.09, "lon": 72.87},
    "DXB": {"name": "Dubai", "lat": 25.25, "lon": 55.36},
    "LHR": {"name": "London Heathrow", "lat": 51.47, "lon": -0.45},
    "JFK": {"name": "New York JFK", "lat": 40.64, "lon": -73.78},
    "ORD": {"name": "Chicago O'Hare", "lat": 41.98, "lon": -87.90},
    "SFO": {"name": "San Francisco", "lat": 37.62, "lon": -122.38},
    "SIN": {"name": "Singapore", "lat": 1.36, "lon": 103.99},
}

_FLIGHTS = [
    ("AI101", "DEL", "LHR", "06:30"), ("AI131", "BOM", "JFK", "02:15"),
    ("EK510", "DXB", "DEL", "09:05"), ("BA142", "LHR", "JFK", "10:45"),
    ("UA901", "ORD", "LHR", "18:20"), ("UA837", "SFO", "SIN", "23:55"),
    ("SQ026", "SIN", "SFO", "08:40"), ("AA100", "JFK", "LHR", "19:00"),
    ("6E205", "BOM", "DEL", "07:50"), ("EK203", "DXB", "JFK", "08:30"),
    ("AI144", "DEL", "SFO", "14:10"), ("BA256", "LHR", "SIN", "21:15"),
    ("UA2", "SFO", "ORD", "12:00"), ("AI687", "DEL", "DXB", "04:20"),
    ("SQ317", "SIN", "LHR", "11:25"),
]
FLIGHTS = [dict(no=n, frm=f, to=t, dep=d) for n, f, t, d in _FLIGHTS]

EVENT_TYPES = {
    "strike": {"label": "Strike", "sev": 60},
    "atc": {"label": "ATC outage", "sev": 75},
    "security": {"label": "Security incident", "sev": 80},
    "ash": {"label": "Volcanic ash", "sev": 95},
    "festival": {"label": "Mass event", "sev": 25},
}

# Simulated weather presets (override live data for an airport)
WEATHER_PRESETS = {
    "storm": {"code": 95, "gust": 95, "precip": 12, "vis": 2500, "label": "thunderstorm"},
    "snow": {"code": 75, "snow": 4, "gust": 55, "vis": 800, "temp": -8, "label": "heavy snow"},
    "fog": {"code": 45, "vis": 300, "label": "dense fog"},
}

CALM = {"temp": 20, "precip": 0, "snow": 0, "code": 1, "wind": 12, "gust": 20, "vis": 10000}
