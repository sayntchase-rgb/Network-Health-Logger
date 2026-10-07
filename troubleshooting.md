\# Network Troubleshooting Case Study



\## Objective



Determine whether a Windows workstation had functioning network and Internet connectivity and isolate differences between IPv4 and IPv6 behavior.



\## Tools Used



\- `ipconfig`

\- `ping`

\- `nslookup`

\- `tracert`

\- `arp -a`



\## Tests and Findings



\### IPv4 Connectivity



A ping test to `8.8.8.8` completed successfully with approximately 10 ms average latency.



This confirmed that the workstation had working IPv4 Internet connectivity.



\### DNS Resolution



`nslookup google.com` successfully returned IP addresses.



This showed that DNS resolution was functioning.



\### Routing



An IPv4 `tracert` successfully reached its destination.



This demonstrated that traffic could travel beyond the local gateway and across multiple routed networks.



\### IPv6 Testing



IPv6 ping and traceroute attempts timed out.



Because IPv4 connectivity and DNS resolution were functioning, the failure did not indicate a complete Internet outage.



Instead, the evidence suggested an IPv6-specific connectivity or routing issue requiring separate investigation.



\### ARP Inspection



`arp -a` was used to inspect devices currently known on the local network, including the default gateway.



\## Troubleshooting Logic



The problem was tested in stages:



1\. Verify local network configuration.

2\. Test direct IP connectivity.

3\. Test DNS resolution.

4\. Inspect the network path.

5\. Compare IPv4 and IPv6 behavior.

6\. Inspect local ARP information.



Testing each component separately prevented an IPv6-specific issue from being incorrectly diagnosed as total network failure.



\## Skills Demonstrated



\- Basic TCP/IP troubleshooting

\- IPv4 versus IPv6 isolation

\- DNS verification

\- Route-path inspection

\- ARP table inspection

\- Evidence-based troubleshooting

\- Technical documentation

