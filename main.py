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

SOFT_REACHED_REBOOT = Gauge(
    "pi3_soft_reached_reboot_bool",
    "Whether soft temperature limit has been reached since last reboot",
    ["whatson"],
)
ARM_FREQ_CAPPED_REBOOT = Gauge(
    "pi3_arm_freq_capped_reboot_bool",
    "Whether arm frequence has been capped since last reboot",
    ["whatson"],
)
THROTTLED_REBOOT = Gauge(
    "pi3_throttled_reboot_bool",
    "Whether throttlign has been enabled since last reboot",
    ["whatson"],
)
UNDER_VOLTAGE_REBOOT = Gauge(
    "pi3_under_voltage_reboot_bool",
    "Whether undervoltage has been detected since last boot",
    ["whatson"],
)
SOFT_REACHED = Gauge(
    "pi3_soft_reached_bool",
    "Whether the soft temperature limit is reached",
    ["whatson"],
)
ARM_FREQ_CAPPED = Gauge(
    "pi3_arm_freq_capped_bool",
    "Whether the arm frequence is being capped",
    ["whatson"],
)
THROTTLED = Gauge(
    "pi3_throttled_bool", "Whether pi3 is being throttled", ["whatson"]
)
UNDER_VOLTAGE = Gauge(
    "pi3_under_voltage_bool", "Whether pi3 detects undervoltage", ["whatson"]
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

        # get throttled
        throttle_reading = check_output(
            "/opt/vc/bin/vcgencmd get_throttled", shell=True
        ).decode()
        [throttle_hex_value] = findall("0x\d+", throttle_reading)

        throttle_value = int(throttle_hex_value, 0)
        soft_reached_reboot = throttle_value & 0b100000000000000000000
        arm_freq_capped_reboot = throttle_value & 0b010000000000000000000
        throttled_reboot = throttle_value & 0b001000000000000000000
        under_voltage_reboot = throttle_value & 0b000100000000000000000
        soft_reached = throttle_value & 0b000000000000000001000
        arm_freq_capped = throttle_value & 0b000000000000000000100
        throttled = throttle_value & 0b000000000000000000010
        under_voltage = throttle_value & 0b000000000000000000001

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
            SOFT_REACHED_REBOOT.clear()
            ARM_FREQ_CAPPED_REBOOT.clear()
            THROTTLED_REBOOT.clear()
            UNDER_VOLTAGE_REBOOT.clear()
            SOFT_REACHED.clear()
            ARM_FREQ_CAPPED.clear()
            THROTTLED.clear()
            UNDER_VOLTAGE.clear()
            last_label = label

        # report
        TEMP.labels(label).set(float(temperature_value))
        SOFT_REACHED_REBOOT.labels(label).set(soft_reached_reboot)
        ARM_FREQ_CAPPED_REBOOT.labels(label).set(arm_freq_capped_reboot)
        THROTTLED_REBOOT.labels(label).set(throttled_reboot)
        UNDER_VOLTAGE_REBOOT.labels(label).set(under_voltage_reboot)
        SOFT_REACHED.labels(label).set(soft_reached)
        ARM_FREQ_CAPPED.labels(label).set(arm_freq_capped)
        THROTTLED.labels(label).set(throttled)
        UNDER_VOLTAGE.labels(label).set(under_voltage)

        # yield
        sleep(0.5)


if __name__ == "__main__":
    run(main)
