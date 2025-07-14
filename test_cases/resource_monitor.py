import threading
import subprocess
import time
import re


class ResourceMonitor(threading.Thread):
    def __init__(self, interval=1):
        super().__init__()
        self.interval = interval
        self.running = False
        self.cpu_usages = []
        self.mem_usages = []
        self.daemon = True

    def get_cpu_usage(self):
        try:
            output = subprocess.check_output(
                "adb shell dumpsys cpuinfo",
                shell=True,
                stderr=subprocess.STDOUT
            ).decode()

            # Parse output without grep
            for line in output.splitlines():
                if "TOTAL" in line:
                    return float(line.strip().split('%')[0])
            return 0.0
        except Exception as e:
            print(f"CPU monitoring error: {str(e)}")
            return 0.0

    def get_mem_usage(self):
        try:
            output = subprocess.check_output(
                "adb shell dumpsys meminfo",
                shell=True,
                stderr=subprocess.STDOUT
            ).decode()

            # Parse output without grep
            for line in output.splitlines():
                if "Used RAM" in line:
                    # Extract first number value (might be in KB)
                    value = re.search(r'(\d[\d,]*)', line.replace(',', ''))
                    if value:
                        value_kb = float(value.group(1))
                        return value_kb / 1024.0  # Convert KB to MB
            return 0.0
        except Exception as e:
            print(f"Memory monitoring error: {str(e)}")
            return 0.0

    def run(self):
        self.running = True
        while self.running:
            cpu = self.get_cpu_usage()
            mem = self.get_mem_usage()
            self.cpu_usages.append(cpu)
            self.mem_usages.append(mem)
            time.sleep(self.interval)

    def stop(self):
        self.running = False
        if self.is_alive():
            self.join(timeout=1.0)

    def get_averages(self):
        cpu_avg = sum(self.cpu_usages) / len(self.cpu_usages) if self.cpu_usages else 0
        mem_avg = sum(self.mem_usages) / len(self.mem_usages) if self.mem_usages else 0

        return cpu_avg, mem_avg