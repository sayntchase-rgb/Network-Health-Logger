import subprocess
import re
from datetime import datetime

target = "8.8.8.8"
log_file = "network_health.log"

result = subprocess.run(
    ["ping", "-n", "1", target],
    capture_output=True,
    text=True
)

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if result.returncode == 0:
    match = re.search(r"time[=<](\d+)ms", result.stdout)

    if match:
        latency = int(match.group(1))

        if latency <= 100:
            status = "HEALTHY"
        else:
            status = "DEGRADED"

        message = f"{timestamp} | {target} | {latency} ms | {status}"

    else:
        message = f"{timestamp} | {target} | latency unavailable | DEGRADED"

else:
    message = f"{timestamp} | {target} | DOWN"

print(message)

with open(log_file, "a") as file:
    file.write(message + "\n")