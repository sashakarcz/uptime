import re
import yaml
import subprocess
from datetime import datetime

# Load the config/domains.yml or .upptimerc.yml file
with open('config/domains.yml', 'r') as file:  # or .upptimerc.yml
    config = yaml.safe_load(file)

# Initialize the results array
results = []

# Function to run a DNS check
def run_dns_check(domain, expected_record, record_type):
    print(f"Running DNS check for {domain} (Type: {record_type}, Expected: {expected_record})")
    try:
        result = subprocess.check_output(["dig", "+short", domain, record_type], text=True).strip().splitlines()

        if not result:
            result = ["No record found"]

        status = "Passed" if set(result) == set(expected_record) else "Failed"
        return {
            "domain": domain,
            "expected": expected_record,
            "actual": result,
            "status": status,
            "timestamp": str(datetime.utcnow())
        }
    except subprocess.CalledProcessError as e:
        print(f"Error during DNS check for {domain}: {str(e)}")
        return {
            "domain": domain,
            "expected": expected_record,
            "actual": ["Error"],
            "status": "Error",
            "timestamp": str(datetime.utcnow())
        }

# Run checks and collect results
for entry in config['domains']:
    domain = entry['domain']
    expected_record = entry['expected_record'] if isinstance(entry['expected_record'], list) else [entry['expected_record']]
    record_type = entry['record_type']
    results.append(run_dns_check(domain, expected_record, record_type))

# Format results in markdown
dns_results_md = "## Live Status\n\n| Domain           | Status     | Expected         | Actual           | Timestamp              |\n"
dns_results_md += "|------------------|------------|------------------|------------------|------------------------|\n"
for res in results:
    dns_results_md += f"| {res['domain']} | {res['status']} | {', '.join(res['expected'])} | {', '.join(res['actual'])} | {res['timestamp']} |\n"

# Update README.md in the Live Status section
with open('README.md', 'r+') as readme_file:
    readme_content = readme_file.read()
    updated_content = re.sub(r"(## Live Status\n\n\| Domain[^\n]+\n(?:\|[^\n]+\n)*)", dns_results_md, readme_content, flags=re.DOTALL)
    
    readme_file.seek(0)
    readme_file.write(updated_content)
    readme_file.truncate()

# Append current results to dns_status.md
with open('history/dns_status.md', 'w') as status_file:
    status_file.write(f"\n### DNS Check on {datetime.utcnow().isoformat()}\n\n")
    status_file.write(dns_results_md)

print("DNS check completed. Results updated in README.md and appended to history/dns_status.md")

