import json
import os
import urllib.request
import base64

GRAFANA_URL = os.getenv("GRAFANA_URL", "http://localhost:3000")
GRAFANA_USER = os.getenv("GRAFANA_USER", "admin")
GRAFANA_PASSWORD = os.environ["GRAFANA_PASSWORD"]

dashboard_file = os.path.join(
    os.path.dirname(__file__), "dashboard.json"
)

with open(dashboard_file, encoding="utf-8") as f:
    dashboard = json.load(f)

dashboard["id"] = None

payload = {
    "dashboard": dashboard,
    "overwrite": True
}

credentials = f"{GRAFANA_USER}:{GRAFANA_PASSWORD}"
token = base64.b64encode(credentials.encode()).decode()

request = urllib.request.Request(
    f"{GRAFANA_URL}/api/dashboards/db",
    data=json.dumps(payload).encode(),
    headers={
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    },
    method="POST"
)

with urllib.request.urlopen(request, timeout=30) as response:
    result = json.load(response)

print("SmartMine AI dashboard installed!")
print("Dashboard URL:", GRAFANA_URL + result["url"])
