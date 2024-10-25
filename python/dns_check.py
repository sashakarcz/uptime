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
        # Run the dig command to get the DNS record
        result = subprocess.check_output(["dig", "+short", domain, record_type], text=True).strip().split('\n')

        if not result:
            result = ["No record found"]

        # Compare the result with the expected record
        if set(result) == set(expected_record):
            print(f"DNS check passed for {domain}")
        else:
            print(f"DNS check failed for {domain}. Got {result}, expected {expected_record}")

        return {domain: {"actual": result, "expected": expected_record, "timestamp": str(datetime.utcnow())}}

    except subprocess.CalledProcessError as e:
        print(f"Error during DNS check for {domain}: {str(e)}")
        return {domain: {"actual": ["Error"], "expected": expected_record, "timestamp": str(datetime.utcnow())}}

# Iterate over the DNS entries in the .upptimerc.yml
for entry in config['dns']['domains']:
    domain = entry['domain']
    expected_record = entry['expected_record']
    record_type = entry['record_type']

    # Run the DNS check
    result = run_dns_check(domain, expected_record, record_type)
    results.append(result)

# Write the results to a YAML file
with open('history/dns_results.yml', 'w') as outfile:
    yaml.dump(results, outfile, default_flow_style=False)

print("DNS check completed. Results written to history/dns_results.yml")
