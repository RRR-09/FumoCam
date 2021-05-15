def run_as_admin():
    from sys import executable as a_executable, argv as a_argv
    from ctypes import windll as a_windll
    from traceback import format_exc as a_fe

    try:
        is_not_admin = not (a_windll.shell32.IsUserAnAdmin())
    except Exception:
        is_not_admin = True
    if is_not_admin:
        print("Packages missing, auto-installing.")
        print("Administrator access required. Acquiring...")
        try:
            run_path = ""
            for i, item in enumerate(a_argv[0:]):
                run_path += f'"{item}"'
            a_windll.shell32.ShellExecuteW(None, "runas", a_executable, run_path, None, 1)
            return False
        except Exception:
            print(a_fe())
    else:
        print("Administrator access acquired.")
        return True


is_admin = run_as_admin()
if not is_admin:
    print("NOT ADMIN, EXITING")
    exit()
from time import sleep
from globals import output_log
from os import path, getcwd
import psutil  # pip install psutil
import clr  # pip install wheel; pip install pythonnet

clr.AddReference(path.join(getcwd(), "resources", "OpenHardwareMonitorLib.dll"))
import OpenHardwareMonitor.Hardware


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
