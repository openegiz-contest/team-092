import json
import random
import time
import argparse
import os

import paho.mqtt.client as mqtt

THING_ID = "smartmine.ai:copper-mine-01"
MQTT_TOPIC = "telemetry/copper-mine-01"
CONTROL_TOPIC = "smartmine/control/scenario"

current_scenario = "NORMAL"


def on_control_message(client, userdata, message):
    global current_scenario

    scenario = message.payload.decode("utf-8").strip().upper()

    if scenario in ("NORMAL", "METHANE_LEAK", "VENTILATION_FAILURE"):
        current_scenario = scenario
        print(f"Scenario changed to: {scenario}", flush=True)

def create_message(temperature, methane, humidity, airflow, fan_status, risk):
    features = {
        "environment": {
            "properties": {
                "temperature_c": temperature,
                "methane_percent": methane,
                "humidity_percent": humidity
            }
        },
        "ventilation": {
            "properties": {
                "fan_status": fan_status,
                "airflow_m3_s": airflow
            }
        },
        "safety": {
            "properties": {
                "risk_level": risk,
                "workers_underground": 12
            }
        }
    }

    return {
        "topic": "smartmine.ai/copper-mine-01/things/twin/commands/modify",
        "path": "/features",
        "value": features
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    client = None

    if not args.dry_run:
        client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id="smartmine-ai-simulator"
        )
        client.connect(os.getenv("MQTT_HOST", "localhost"), int(os.getenv("MQTT_PORT", "1883")))
        client.loop_start()
        client.message_callback_add(CONTROL_TOPIC, on_control_message)
        client.subscribe(CONTROL_TOPIC)
    step = 0

    try:
        while args.steps == 0 or step < args.steps:
            if current_scenario == "METHANE_LEAK":
                temperature = round(random.uniform(28, 32), 1)
                methane = round(random.uniform(1.5, 1.8), 2)
                humidity = round(random.uniform(45, 75), 1)

            elif current_scenario == "VENTILATION_FAILURE":
                temperature = round(random.uniform(30, 35), 1)
                methane = round(random.uniform(1.3, 1.8), 2)
                humidity = round(random.uniform(60, 80), 1)

            else:
                temperature = round(random.uniform(22, 34), 1)
                methane = round(random.uniform(0.1, 1.8), 2)
                humidity = round(random.uniform(45, 75), 1)

            if current_scenario == "VENTILATION_FAILURE":
                risk = "HIGH"
                fan_status = "OFF"
                airflow = 0
            elif methane >= 1.0 or temperature >= 30:
                risk = "HIGH"
                fan_status = "BOOST"
                airflow = 30
            elif methane >= 0.5 or temperature >= 27:
                risk = "MEDIUM"
                fan_status = "ON"
                airflow = 22
            else:
                risk = "LOW"
                fan_status = "ON"
                airflow = 18

            message = create_message(
                temperature, methane, humidity,
                airflow, fan_status, risk
            )

            if args.dry_run:
                print(json.dumps(message, indent=2))
            else:
                client.publish(MQTT_TOPIC, json.dumps(message))
                print(
                    f"Temperature: {temperature} C | "
                    f"Methane: {methane}% | "
                    f"Risk: {risk} | Fan: {fan_status}",
                    flush=True
                )

            step += 1
            if args.steps == 0 or step < args.steps:
                time.sleep(2)

    except KeyboardInterrupt:
        print("\nSimulator stopped.")

    finally:
        if client:
            client.loop_stop()
            client.disconnect()


if __name__ == "__main__":
    main()
