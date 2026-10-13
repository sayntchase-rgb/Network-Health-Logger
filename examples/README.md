# Customer Diagnostic Demo

`customer_demo.csv` is synthetic example data for demonstrating the customer-report workflow. It is not real customer data.

From the repository root, run:

```powershell
py report_generator.py `
  --csv-file examples\customer_demo.csv `
  --output-prefix reports\demo_client `
  --target 8.8.8.8 `
  --client-name "Demo Client" `
  --site-name "Home Office" `
  --prepared-by "Network Technician" `
  --notes "Intermittent connection reported."
```

Expected output files:

```text
reports\demo_client.txt
reports\demo_client.html
```

Use the demo to show the workflow without exposing real customer information. The sample intentionally includes healthy, degraded, and down observations so the generated report demonstrates findings and recommendations.
