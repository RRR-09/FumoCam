def RunAsAdmin():
    from sys import executable as a_executable, argv as a_argv 
    from ctypes import windll as a_windll
    from traceback import format_exc as a_fe

    isNotAdmin = False
    try:
        isNotAdmin=not(a_windll.shell32.IsUserAnAdmin())
    except:
        isNotAdmin=True
    if isNotAdmin:
      print("Packages missing, auto-installing.")
      print("Administrator access required. Acquiring...")
      try:
        runDir = ""
        for i, item in enumerate(a_argv[0:]):
          runDir += '"' + item + '" '
        a_windll.shell32.ShellExecuteW(None, "runas", a_executable, runDir, None, 1)
        return False
      except:
        print(a_fe())
    else:
      print("Administrator access acquired.")
      return True


isAdmin = RunAsAdmin()
if not isAdmin:
    print("NOT ADMIN, EXITING")
    exit()
from time import sleep
from globals import output_log
import globals
from os import path, getcwd
import psutil #pip install psutil
import clr #pip install wheel; pip install pythonnet
from traceback import format_exc

clr.AddReference(path.join(getcwd(), "resources", "OpenHardwareMonitorLib.dll"))
from OpenHardwareMonitor.Hardware import Computer


# def report(c):
    # for hardware in c.Hardware:
        # #print(i.get_HardwareType())
        # hardware.Update()
    # report = c.GetReport()
    # print(report)
    # gpu_temp = report.split("Name: NVIDIA GeForce GTX 1650",1)[-1].split("Sensor[0].CurrentTemp: ")[-1].split("\n",1)[0]
    # print(gpu_temp)


def get_temps(c):
    cpu_temp = -1
    gpu_temp = -1
    for hardware in c.Hardware:
        hardware.Update()
        for sensor in hardware.Sensors:        
            if "temperature" in str(sensor.Identifier):
                sensor_name = sensor.get_Name()
                #print(sensor_name)
                #try:
                #    print(sensor.get_Value())
                #except:
                #    print("ERROR")
                if sensor_name == "CPU Package":
                    #print(dir(sensor.Values))
                    cpu_temp = sensor.get_Value()
                    if gpu_temp != -1:
                        break
                elif sensor_name == "GPU Core":
                    gpu_temp = sensor.get_Value()
                    if cpu_temp != -1:
                        break
                        
        if gpu_temp != -1 and cpu_temp != -1:
            break
    #cpu_temp = "ERROR" if None or -1 else cpu_temp
    return cpu_temp, gpu_temp


#if __name__ == "__main__":
c = Computer()
c.CPUEnabled = True # get the Info about CPU
c.GPUEnabled = True # get the Info about GPU
c.FanControllerEnabled = True # get the Info about GPU
c.MainBoardEnabled = True # get the Info about GPU
c.RAMEnabled = True # get the Info about GPU
c.Open()

while True:
    cpu_temp, gpu_temp = get_temps(c)
    gpu_temp_msg = f"GPU: {gpu_temp}C"
    cpu_temp_msg = f"CPU: {cpu_temp}C"
    output_log("cpu_temp", cpu_temp_msg)
    output_log("cpu_temp", gpu_temp_msg)
    output_log("cpu+gpu_temp", f"{cpu_temp_msg} | {gpu_temp_msg}")
    print(gpu_temp_msg, cpu_temp_msg)
    plugged = True
    percent = "-1"
    battery = psutil.sensors_battery()
    if battery == None:
        output_log("power_failure", "[WARN] No battery detected!")
        output_log("power_restored", "")
        plugged = True
        percent = "-1"
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