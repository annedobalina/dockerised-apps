import subprocess
import json
import time
import os
from influxdb import InfluxDBClient

# Configuration from environment variables
INFLUXDB_HOST = os.getenv("INFLUXDB_HOST", "influxdb")
INFLUXDB_PORT = int(os.getenv("INFLUXDB_PORT", 8086))
INFLUXDB_DB = os.getenv("INFLUXDB_DB", "speedtest_db")
INTERVAL_MINUTES = int(os.getenv("INTERVAL_MINUTES", 10))

def run_speedtest():
    try:
        result = subprocess.run(['speedtest-cli', '--json'], stdout=subprocess.PIPE, check=True)
        return json.loads(result.stdout.decode('utf-8'))
    except Exception as e:
        print(f"Speedtest error: {e}", flush=True)
        return None

def write_to_influxdb(data):
    if not data:
        return

    client = InfluxDBClient(
        host=INFLUXDB_HOST,
        port=INFLUXDB_PORT,
        database=INFLUXDB_DB
    )

    # Create DB if it doesn't exist
    if INFLUXDB_DB not in [db['name'] for db in client.get_list_database()]:
        client.create_database(INFLUXDB_DB)

    json_body = [{
        "measurement": "speedtest",
        "tags": {
            "host": "raspberry_pi",
            "server": data.get('server', {}).get('sponsor', 'unknown')
        },
        "fields": {
            "download_speed": round(data.get('download', 0.0) / 1e6, 2),
            "upload_speed": round(data.get('upload', 0.0) / 1e6, 2),
            "ping": round(data.get('ping', 0.0), 2),
            "jitter": round(data.get('jitter', 0.0), 2),
            "loss": round(data.get('packetLoss', 0.0), 2)
        }
    }]
    client.write_points(json_body)
    print("Speedtest written to InfluxDB.\n", flush=True)

def main():
    while True:
        print("Running speedtest...\n", flush=True)
        data = run_speedtest()
        if data:
            download = round(data.get('download', 0.0) / 1e6, 2)
            upload = round(data.get('upload', 0.0) / 1e6, 2)
            ping = round(data.get('ping', 0.0), 2)
            jitter = round(data.get('jitter', 0.0), 2)
            loss = round(data.get('packetLoss', 0.0), 2)
            server = data.get('server', {}).get('sponsor', 'unknown')

            print("Speedtest Results:", flush=True)
            print(f"  Server     : {server}", flush=True)
            print(f"  Download   : {download} Mbps", flush=True)
            print(f"  Upload     : {upload} Mbps", flush=True)
            print(f"  Ping       : {ping} ms", flush=True)
            print(f"  Jitter     : {jitter} ms", flush=True)
            print(f"  Packet Loss: {loss}%\n", flush=True)

            write_to_influxdb(data)
        else:
            print("Speedtest failed, skipping write.\n", flush=True)

        print(f"Waiting {INTERVAL_MINUTES} minutes...\n", flush=True)
        time.sleep(INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    main()
