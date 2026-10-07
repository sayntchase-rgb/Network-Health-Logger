import subprocess
import re

target = "8.8.8.8"

result = subprocess.run(
    ["ping", "-n", "1", target],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    match = re.search(r"time[=<](\d+)ms", result.stdout)

    if match:
        latency = int(match.group(1))

        if latency <= 100:
            status = "HEALTHY"
        else:
            status = "DEGRADED"

        print(f"{target} | {latency} ms | {status}")
    else:
        print(f"{target} | latency unavailable | DEGRADED")
else:
    print(f"{target} | DOWN")