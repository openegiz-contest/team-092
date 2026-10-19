
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import paho.mqtt.client as mqtt

state = {
    "temperature": 25.0,
    "methane": 0.2,
    "humidity": 55.0,
    "airflow": 18,
    "fan": "ON",
    "risk": "LOW",
    "workers": 12,
    "connected": False,
}

lock = threading.Lock()

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SmartMine AI | Digital Mine Map</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#0b1220;color:#e5edf8;font-family:Arial,sans-serif}
header{padding:22px 5%;background:#111c2e;border-bottom:1px solid #29384e}
h1{margin:0 0 8px;font-size:27px}
header p{margin:0;color:#9fb0c7}
main{max-width:1200px;margin:auto;padding:24px}
.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.card{background:#152238;border:1px solid #29384e;border-radius:12px;padding:17px}
.label{color:#9fb0c7;font-size:13px}
.value{font-size:27px;font-weight:bold;margin-top:10px}
.unit{font-size:14px;color:#9fb0c7}
.panel{margin-top:20px;background:#111c2e;border:1px solid #29384e;border-radius:14px;padding:18px}
h2{font-size:19px;margin:0 0 15px}
svg{width:100%;height:auto;display:block}
.tunnel{fill:none;stroke:#52657e;stroke-width:27;stroke-linecap:round;stroke-linejoin:round}
.centerline{fill:none;stroke:#9aabc0;stroke-width:2;stroke-dasharray:9 8}
.zone{fill:#183e36;stroke:#38b887;stroke-width:3}
.zone.medium{fill:#49391c;stroke:#f3b746}
.zone.high{fill:#4b2029;stroke:#ff5867}
.sensor{fill:#e9f2ff;stroke:#34465e;stroke-width:3}
.fan{fill:#233f61;stroke:#67b7ff;stroke-width:3}
.maptext{fill:#e5edf8;font-size:15px}
.small{fill:#b5c5da;font-size:12px}
.legend{display:flex;gap:18px;flex-wrap:wrap;color:#b5c5da;font-size:13px}
.dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px}
.status{padding:7px 12px;border-radius:7px;font-weight:bold;display:inline-block}
.low{background:#164d3a;color:#8af0c0}
.mediumBadge{background:#604618;color:#ffda86}
.high{background:#67232d;color:#ffadb5}
footer{color:#91a3ba;font-size:12px;margin-top:16px}
@media(max-width:700px){.cards{grid-template-columns:repeat(2,1fr)}main{padding:14px}.value{font-size:22px}}
</style>
</head>
<body>
<header>
<h1>SmartMine AI | Underground Mine</h1>
<p>Digital twin monitoring · Copper Mine 01</p>
</header>
<main>
<div class="cards">
<div class="card"><div class="label">Temperature</div><div class="value"><span id="temp">--</span> <span class="unit">°C</span></div></div>
<div class="card"><div class="label">Methane</div><div class="value"><span id="methane">--</span> <span class="unit">%</span></div></div>
<div class="card"><div class="label">Airflow</div><div class="value"><span id="airflow">--</span> <span class="unit">m³/s</span></div></div>
<div class="card"><div class="label">Safety risk</div><div class="value"><span id="risk" class="status low">LOW</span></div></div>
</div>
<div class="panel">
<h2>Mine layout · illustrative schematic</h2>
<svg viewBox="0 0 900 430" role="img" aria-label="Schematic underground mine map">
<path class="tunnel" d="M70 215 H830 M180 215 V105 H365 V215 M365 215 V335 H570 V215 M650 215 V105 H790 V215"/>
<path class="centerline" d="M70 215 H830 M180 215 V105 H365 V215 M365 215 V335 H570 V215 M650 215 V105 H790 V215"/>
<circle id="zoneA" class="zone" cx="180" cy="215" r="32"/>
<circle id="zoneB" class="zone" cx="440" cy="215" r="32"/>
<circle id="zoneC" class="zone" cx="700" cy="215" r="32"/>
<circle class="sensor" cx="180" cy="215" r="8"/>
<circle class="sensor" cx="440" cy="215" r="8"/>
<circle class="sensor" cx="700" cy="215" r="8"/>
<rect class="fan" x="320" y="85" width="42" height="38" rx="7"/>
<path d="M331 94 L352 104 L331 114 Z" fill="#67b7ff"/>
<rect class="fan" x="570" y="315" width="42" height="38" rx="7"/>
<path d="M581 324 L602 334 L581 344 Z" fill="#67b7ff"/>
<text class="maptext" x="130" y="270">Zone A</text>
<text class="maptext" x="390" y="270">Zone B</text>
<text class="maptext" x="650" y="270">Zone C</text>
<text class="small" x="295" y="72">Ventilation fan 1</text>
<text class="small" x="545" y="300">Ventilation fan 2</text>
<text class="small" x="72" y="190">Entrance</text>
<text class="small" x="730" y="190">Mining area</text>
<text class="small" x="35" y="390">Sensors: methane · temperature · humidity</text>
<text class="small" x="35" y="410">Illustrative layout — not a surveyed mine map</text>
</svg>
<div class="legend">
<span><i class="dot" style="background:#38b887"></i>Low risk</span>
<span><i class="dot" style="background:#f3b746"></i>Medium risk</span>
<span><i class="dot" style="background:#ff5867"></i>High risk</span>
<span>➜ Blue symbols: ventilation fans</span>
</div>
</div>
<div class="panel">
<h2>Live status</h2>
<p>Humidity: <strong id="humidity">--</strong>%</p>
<p>Ventilation fan: <strong id="fan">--</strong></p>
<p>Workers underground: <strong id="workers">--</strong></p>
<p>MQTT connection: <strong id="connection">Waiting for telemetry</strong></p>
<footer>Values come from the SmartMine simulator. This prototype is not certified for real mine safety decisions.</footer>
</div>
</main>
<script>
async function update(){
 try{
  const response=await fetch('/api/state',{cache:'no-store'});
  const s=await response.json();
  document.getElementById('temp').textContent=s.temperature;
  document.getElementById('methane').textContent=s.methane;
  document.getElementById('humidity').textContent=s.humidity;
  document.getElementById('airflow').textContent=s.airflow;
  document.getElementById('fan').textContent=s.fan;
  document.getElementById('workers').textContent=s.workers;
  document.getElementById('connection').textContent=s.connected?'Receiving telemetry':'Waiting for telemetry';
  const risk=String(s.risk||'LOW');
  const badge=document.getElementById('risk');
  badge.textContent=risk;
  badge.className='status '+(risk==='HIGH'?'high':risk==='MEDIUM'?'mediumBadge':'low');
  ['zoneA','zoneB','zoneC'].forEach(id=>{
    const el=document.getElementById(id);
    el.setAttribute('class','zone'+(risk==='HIGH'?' high':risk==='MEDIUM'?' medium':''));
  });
 }catch(e){
  document.getElementById('connection').textContent='API unavailable';
 }
}
update();
setInterval(update,2000);
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/state":
            with lock:
                body = json.dumps(state).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        body = HTML.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print("HTTP:", fmt % args)


def on_connect(client, userdata, flags, reason_code, properties):
    print("MQTT connection:", reason_code)
    if reason_code == 0:
        client.subscribe("telemetry/copper-mine-01")


def on_message(client, userdata, msg):
    try:
        message = json.loads(msg.payload.decode())
        features = message.get("value", {})
        env = features.get("environment", {}).get("properties", {})
        vent = features.get("ventilation", {}).get("properties", {})
        safety = features.get("safety", {}).get("properties", {})

        with lock:
            state.update({
                "temperature": env.get("temperature_c", state["temperature"]),
                "methane": env.get("methane_percent", state["methane"]),
                "humidity": env.get("humidity_percent", state["humidity"]),
                "airflow": vent.get("airflow_m3_s", state["airflow"]),
                "fan": vent.get("fan_status", state["fan"]),
                "risk": safety.get("risk_level", state["risk"]),
                "workers": safety.get("workers_underground", state["workers"]),
                "connected": True,
            })
    except (ValueError, TypeError) as exc:
        print("Invalid telemetry:", exc)


def main():
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="smartmine-map-dashboard"
    )
    client.on_connect = on_connect
    client.on_message = on_message
    host = os.getenv("MQTT_HOST", "localhost")
    port = int(os.getenv("MQTT_PORT", "1883"))
    client.connect(host, port)
    client.loop_start()

    server = ThreadingHTTPServer(("0.0.0.0", 8080), Handler)
    print("Mine map available on port 8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
