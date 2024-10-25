import yaml
import subprocess
from datetime import datetime
import re

# Load the .upptimerc.yml file
with open('.upptimerc.yml', 'r') as file:
    config = yaml.safe_load(file)

# Initialize the results array
results = []

# Function to run a DNS check
def run_dns_check(domain, expected_record, record_type):
    print(f"Running DNS check for {domain} (Type: {record_type}, Expected: {expected_record})")
    try:
        # Run the dig command to get the DNS record
        result = subprocess.check_output(["dig", "+short", domain, record_type], text=True).strip().splitlines()

        if not result:
            result = ["No record found"]

        # Determine if the DNS check passed or failed
        status = "Passed" if result == expected_record else "Failed"
        return {
            "domain": domain,
            "actual": result,
            "expected": expected_record,
            "timestamp": datetime.utcnow().isoformat(),
            "status": status
        }

    except subprocess.CalledProcessError as e:
        print(f"Error during DNS check for {domain}: {str(e)}")
        return {
            "domain": domain,
            "actual": ["Error"],
            "expected": expected_record,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "Error"
        }

# Iterate over entries in the sites section and filter DNS checks
for entry in config['sites']:
    if 'domain' in entry:  # Check for DNS-specific keys
        domain = entry['domain']
        expected_record = entry.get('expected_record', [])
        record_type = entry.get('record_type', "A")  # Default to A record if unspecified

        # Run the DNS check
        result = run_dns_check(domain, expected_record, record_type)
        results.append(result)

# Write the results to a YAML file
with open('history/dns_results.yml', 'w') as outfile:
    yaml.dump(results, outfile, default_flow_style=False)

print("DNS check completed. Results written to history/dns_results.yml")

# Format results in markdown for Live DNS Status
dns_results_md = "## Live DNS Status\n\n| Domain           | Status     | Expected         | Actual           | Timestamp              |\n"
dns_results_md += "|------------------|------------|------------------|------------------|------------------------|\n"
for res in results:
    dns_results_md += f"| {res['domain']} | {res['status']} | {', '.join(res['expected'])} | {', '.join(res['actual'])} | {res['timestamp']} |\n"

# Update README.md in the Live DNS Status section
with open('README.md', 'r+') as readme_file:
    readme_content = readme_file.read()
    # Insert new DNS status table
    updated_content = re.sub(
        r"(## Live DNS Status\n\n\| Domain[^\n]+\n(?:\|[^\n]+\n)*)",
        dns_results_md,
        readme_content,
        flags=re.DOTALL
    )
    readme_file.seek(0)
    readme_file.write(updated_content)
    readme_file.truncate()

# Write current results to dns_status.md
with open('history/dns_status.md', 'w') as status_file:
    status_file.write(f"\n### DNS Check on {datetime.utcnow().isoformat()}\n\n")
    status_file.write(dns_results_md)

print("DNS check completed. Results updated in README.md and appended to history/dns_status.md")
