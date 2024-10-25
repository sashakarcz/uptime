import yaml
import subprocess
from datetime import datetime

# Load the .upptimerc.yml file
with open('.upptimerc.yml', 'r') as file:
    config = yaml.safe_load(file)

# Initialize the results array
results = []

# Function to run a DNS check
def run_dns_check(domain, expected_record, record_type):
    print(f"Running DNS check for {domain} (Type: {record_type}, Expected: {expected_record})")
    try:
        result = subprocess.check_output(["dig", "+short", domain, record_type], text=True).strip().split('\n')

        if not result:
            result = ["No record found"]

        # Check if DNS results match expectations
        status = "✅ Passed" if set(result) == set(expected_record) else "❌ Failed"
        return {
            "domain": domain,
            "status": status,
            "actual": result,
            "expected": expected_record,
            "timestamp": str(datetime.utcnow())
        }

    except subprocess.CalledProcessError as e:
        print(f"Error during DNS check for {domain}: {str(e)}")
        return {
            "domain": domain,
            "status": "❌ Error",
            "actual": ["Error"],
            "expected": expected_record,
            "timestamp": str(datetime.utcnow())
        }

# Run checks and save results
for entry in config['dns']['domains']:
    domain = entry['domain']
    expected_record = entry['expected_record']
    record_type = entry['record_type']
    result = run_dns_check(domain, expected_record, record_type)
    results.append(result)

# Write results to DNS results markdown file
with open('history/dns_status.md', 'w') as md_file:
    md_file.write("# DNS Monitoring Status\n\n")
    md_file.write("| Domain           | Status     | Expected         | Actual           | Timestamp              |\n")
    md_file.write("|------------------|------------|------------------|------------------|------------------------|\n")
    for res in results:
        md_file.write(
            f"| {res['domain']} | {res['status']} | {', '.join(res['expected'])} | {', '.join(res['actual'])} | {res['timestamp']} |\n"
        )

print("DNS check completed. Results written to history/dns_status.md")

