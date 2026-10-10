from datetime import datetime

from chase_core.networking.health import append_log, format_health_line, ping_host


TARGET = "8.8.8.8"
LOG_FILE = "network_health.log"


def main() -> None:
    ping = ping_host(TARGET)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = format_health_line(timestamp, TARGET, ping)

    print(message)
    append_log(message, LOG_FILE)


if __name__ == "__main__":
    main()
