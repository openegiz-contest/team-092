
# SmartMine AI — Underground Mine Digital Twin

SmartMine AI is a real-time digital twin prototype for monitoring safety conditions in an underground copper mine.

Built for the OpenEgiz Digital Mine contest.

## Project Overview

SmartMine AI simulates underground mine conditions and visualizes them using a digital twin and a real-time dashboard.

The prototype monitors:
- Temperature (°C)
- Methane concentration (%)
- Humidity (%)
- Ventilation status and airflow
- Underground worker count
- Safety risk level (LOW, MEDIUM, HIGH)

The current prototype uses simulated sensor data and explainable rule-based risk detection. It does not use a trained machine-learning model.

## Technologies

- Python — sensor simulation and safety rules
- MQTT / Mosquitto — telemetry messaging
- Eclipse Ditto — digital twin
- InfluxDB — time-series data storage
- Grafana — real-time monitoring dashboard
- Docker Compose — deployment
- OpenEgiz — digital twin platform

## Requirements

- Docker Desktop with Docker Compose
- Git
- Python 3
- GNU Make
- Bash
- Internet connection for the initial build

## Quick Start

Clone the repository:

```bash
git clone https://github.com/openegiz-contest/team-092.git
cd team-092
```

Start the platform, create the digital twin, install the dashboard, and launch the simulator:

```bash
bash team/smartmine/start.sh
```

The initial build may take several minutes.

## Dashboard

Open Grafana:

http://localhost:3000

The dashboard is titled:

**SmartMine AI | Underground Mine Safety**

Grafana credentials are generated in:

`deploy/compose/.env`

Do not commit this file or share its secrets.

## How It Works

1. The Python simulator generates synthetic mine sensor measurements.
2. Measurements are published through MQTT.
3. The OpenEgiz platform processes the telemetry.
4. Eclipse Ditto represents the mine as a digital twin.
5. InfluxDB stores time-series measurements.
6. Grafana displays mine conditions and safety indicators.

## Safety Logic

The prototype classifies safety risk based on methane concentration and temperature.

| Risk | Conditions |
|---|---|
| HIGH | Methane ≥ 1.0% or temperature ≥ 30°C |
| MEDIUM | Methane ≥ 0.5% or temperature ≥ 27°C |
| LOW | Otherwise |

The ventilation simulator increases airflow when conditions become unsafe.

These thresholds are demonstration rules only and must not be used for real mine safety decisions.

## Project Files

| File | Purpose |
|---|---|
| `team/smartmine/simulator.py` | Sensor simulation and risk detection |
| `team/smartmine/twins.json` | Digital twin definition |
| `team/smartmine/setup_twins.py` | Digital twin initialization |
| `team/smartmine/dashboard.json` | Grafana dashboard |
| `team/smartmine/setup_dashboard.py` | Dashboard installation |
| `team/smartmine/compose.yml` | Simulator container |
| `team/smartmine/start.sh` | Automated startup |
| `presentation.pdf` | Contest presentation |

## Limitations

SmartMine AI is a proof-of-concept prototype. All sensor data is synthetic. The risk detection logic is rule-based, not predictive machine learning. The system has not been validated for real-world mining operations.

## License

See the repository's LICENSE file.


## Interactive Mine Map and What-if Simulation

SmartMine AI includes a live underground mine map available at:

http://localhost:8082

The map displays temperature, methane concentration, airflow,
ventilation status, and safety risk using MQTT telemetry.

### What-if scenarios

- Normal Mode: simulates normal mine operation.
- Methane Leak: simulates elevated methane concentration.
- Ventilation Failure: simulates fan shutdown and zero airflow.

Scenario buttons send commands through MQTT to the simulator.
Updated telemetry is reflected on the map and can be monitored
through Eclipse Ditto and Grafana.

This is an educational simulation, not a certified mine safety system.
The mine layout is illustrative, and all displayed zones currently
share the same overall risk level.
