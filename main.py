from subprocess import check_output
from re import findall
from time import sleep
import os
from clize import run
from prometheus_client import Gauge, start_http_server

# prometheus entrypoint
TEMP = Gauge(
    "pi3_temperature_celsius", "The core temperature of Pi3", ["whatson"]
)


def main(*, tag_file: str = None):
    # data are exposed through http
    start_http_server(int(os.environ["SERVICE_PORT"]))

    # track label and discontinue when changed
    last_label = None
    while True:
        # get the temperature
        temperature_reading = check_output(
            "/opt/vc/bin/vcgencmd measure_temp", shell=True
        ).decode()
        [temperature_value] = findall("\d+\.\d+", temperature_reading)

        # get the whatson tag
        label = "unknown"
        try:
            with open(tag_file) as tag:
                [label] = tag.read().splitlines()
        except:
            pass

        # discontinue if needed
        if last_label is None or last_label != label:
            TEMP.clear()
            last_label = label

        # report
        TEMP.labels(label).set(float(temperature_value))

        # yield
        sleep(0.5)


if __name__ == "__main__":
    run(main)
