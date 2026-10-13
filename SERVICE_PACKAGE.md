# Network Health Diagnostic Package V1

This document turns Network Health Logger into a small, testable service offer. The goal is to validate whether people will pay for a clear network-health diagnosis before building a larger monitoring product.

## Offer

**Network Health Diagnostic**

A lightweight diagnostic service for people experiencing intermittent internet outages, latency spikes, unstable work-from-home connections, gaming lag, or unreliable connected devices.

### Introductory price

- **$75** for the first validation customers
- Raise pricing only after real customer feedback shows the report and recommendations consistently provide value

The introductory price is a business experiment, not a fixed market price.

## Customer receives

1. Network-health monitoring data collected over an agreed test period
2. A structured CSV history
3. A customer-facing TXT report
4. A customer-facing HTML report
5. Uptime and observed probe-loss summary
6. Minimum, average, and maximum latency
7. HEALTHY / DEGRADED / DOWN counts
8. Observed outage-event summary
9. Plain-language findings
10. Suggested next diagnostic steps

## Good-fit problems

- Internet drops at unpredictable times
- Video calls freeze or disconnect
- Gaming latency spikes
- Security cameras or smart devices lose connectivity
- A home office feels unreliable but the failure pattern is unclear
- A customer wants evidence before contacting an ISP or replacing equipment

## Current scope

Version 1 does **not** claim to identify every root cause automatically. The current logger performs one ICMP probe per execution and uses those observations to build a historical availability and latency picture.

The service is intended to answer:

- When did failures occur?
- How often did the selected target become unreachable?
- Was latency elevated during the monitoring period?
- Is there enough evidence to justify deeper local-network or ISP troubleshooting?

## Not included

- Penetration testing or security auditing
- Wi-Fi RF site surveys
- ISP SLA certification
- Guaranteed root-cause identification
- Packet capture of customer traffic
- Credential collection
- Changes to routers, firewalls, or customer equipment without separate approval

## Service workflow

### 1. Intake

Record:

- customer name
- site/location label
- reported symptom
- approximate times the problem usually occurs
- whether the affected device uses Ethernet or Wi-Fi

### 2. Establish monitoring target

Use a stable target appropriate for the diagnostic question. The default public target is `8.8.8.8`, but a gateway or other authorized target may be more useful when separating local connectivity from upstream internet connectivity.

### 3. Collect observations

Run the logger repeatedly over the agreed test period. Scheduling is external to the current application; Windows Task Scheduler or another authorized scheduler can invoke the script at a chosen interval.

Example:

```powershell
py network_health_logger.py --target 8.8.8.8 --csv-file customer_data\client01.csv
```

### 4. Generate the customer report

```powershell
py report_generator.py `
  --csv-file customer_data\client01.csv `
  --output-prefix reports\client01_network_health `
  --target 8.8.8.8 `
  --client-name "Demo Client" `
  --site-name "Home Office" `
  --prepared-by "Network Technician" `
  --notes "Customer reports intermittent evening disconnects."
```

The command creates both `.txt` and `.html` reports.

### 5. Review the result

Explain what was actually observed. Separate measured facts from hypotheses. Use the generated recommendations as starting points, not automatic proof of root cause.

### 6. Capture a case study

With identifying details removed, document:

- reported problem
- monitoring method
- number of checks
- important findings
- actions recommended
- eventual resolution, if known

This converts each completed diagnostic into portfolio evidence and product feedback.

## Validation metrics

Track these for the first 10 prospects:

- prospects contacted
- people who describe a matching problem
- demos performed
- paid diagnostics
- price objections
- report usefulness feedback
- repeat or referral requests

The first milestone is **one real paid diagnostic**, not a larger feature list.

## Upgrade path

Only add features that solve problems confirmed by users. Likely future candidates include:

1. scheduled continuous monitoring
2. multi-probe sampling per interval
3. multiple simultaneous targets
4. gateway-versus-internet comparison
5. charts and trend visualization
6. alerts
7. recurring managed monitoring

That sequence moves the project from a portfolio script toward a productized service without prematurely building a full SaaS platform.
