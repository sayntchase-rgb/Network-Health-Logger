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
        print(f"{target} is reachable - {latency} ms")
    else:
        print(f"{target} is reachable - latency unavailable")
else:
    print(f"{target} is unreachable")
