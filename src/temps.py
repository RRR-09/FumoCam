from time import sleep

import clr
import psutil
from System.IO import FileNotFoundException  # type: ignore

from config import RESOURCES_PATH
from utilities import output_log, run_as_admin

OPEN_HARDWARE_MONITOR_PATH = str(RESOURCES_PATH / "OpenHardwareMonitorLib.dll")
try:
    clr.AddReference(OPEN_HARDWARE_MONITOR_PATH)
except FileNotFoundException:
    raise Exception(
        "OpenHardwareMonitorLib.dll not found! Are you sure you're running from the directory this python script is in?"
        f"\n({OPEN_HARDWARE_MONITOR_PATH})"
    )
# Ignore "Import "OpenHardwareMonitor.Hardware" could not be resolved", is imported dynamically by above line
# Ignore "module level import not at top of file", is impossible to be before clr.AddReference
import OpenHardwareMonitor.Hardwaremodule  # type: ignore # noqa: E402

run_as_admin()


def get_temps(computer):
    cpu_temp = -1
    gpu_temp = -1
    for hardware in computer.Hardware:
        hardware.Update()
        for sensor in hardware.Sensors:
            if "temperature" in str(sensor.Identifier):
                sensor_name = sensor.get_Name()
                if sensor_name == "CPU Package":
                    cpu_temp = sensor.get_Value()
                    if gpu_temp != -1:
                        break
                elif sensor_name == "GPU Core":
                    gpu_temp = sensor.get_Value()
                    if cpu_temp != -1:
                        break

        if gpu_temp != -1 and cpu_temp != -1:
            break
    return cpu_temp, gpu_temp


def main():
    this_computer = OpenHardwareMonitor.Hardware.Computer()
    this_computer.CPUEnabled = True  # get the Info about CPU
    this_computer.GPUEnabled = True  # get the Info about GPU
    this_computer.FanControllerEnabled = True  # get the Info about GPU
    this_computer.MainBoardEnabled = True  # get the Info about GPU
    this_computer.RAMEnabled = True  # get the Info about GPU
    this_computer.Open()

    while True:
        cpu_temp, gpu_temp = get_temps(this_computer)
        gpu_temp_msg = f"GPU: {gpu_temp}C"
        cpu_temp_msg = f"CPU: {cpu_temp}C"
        output_log("cpu_temp", cpu_temp_msg)
        output_log("cpu_temp", gpu_temp_msg)
        output_log("cpu+gpu_temp", f"{cpu_temp_msg} | {gpu_temp_msg}")
        print(gpu_temp_msg, cpu_temp_msg)
        battery = psutil.sensors_battery()
        if battery is None:
            output_log("power_failure", "[WARN] No battery detected!")
            output_log("power_restored", "")
            sleep(1)
            continue

        plugged = battery.power_plugged
        percent = str(battery.percent)
        if plugged:
            if int(battery.percent) > 90:
                battery_status = ""
            else:
                battery_status = f"[WARN] Recent power failure | {percent}% recharged"
            output_log("power_restored", battery_status)
            output_log("power_failure", "")
        else:
            battery_status = f"[WARN] POWER FAILURE | {percent}% BATTERY REMAINING"
            output_log("power_failure", battery_status)
            output_log("power_restored", "")
        if battery_status != "":
            print(battery_status)
        sleep(1)


if __name__ == "__main__":
    main()
