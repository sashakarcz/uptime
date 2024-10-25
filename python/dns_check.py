import yaml
import subprocess
from datetime import datetime

# Load the config/domains.yml file
with open('config/domains.yml', 'r') as file:
    config = yaml.safe_load(file)

# Initialize the results array
results = []

# Function to run a DNS check
def run_dns_check(domain, expected_records, record_type):
    print(f"Running DNS check for {domain} (Type: {record_type}, Expected: {expected_records})")
    try:
        # Run the dig command to get the DNS record
        result = subprocess.check_output(["dig", "+short", domain, record_type], text=True).strip().split("\n")

        if not result or result == ['']:
            result = ["No record found"]

        # Check if actual matches any of the expected records
        matched = all(r in expected_records for r in result) and all(e in result for e in expected_records)
        if matched:
            print(f"DNS check passed for {domain}")
        else:
            print(f"DNS check failed for {domain}. Got {result}, expected {expected_records}")

        return {domain: {
            "actual": result,
            "expected": expected_records,
            "timestamp": str(datetime.utcnow())
        }}

    except subprocess.CalledProcessError as e:
        print(f"Error during DNS check for {domain}: {str(e)}")
        return {domain: {
            "actual": ["Error"],
            "expected": expected_records,
            "timestamp": str(datetime.utcnow())
        }}

# Iterate over the DNS entries in config/domains.yml
for entry in config['domains']:
    domain = entry['domain']
    expected_record = entry['expected_record']
    
    # Ensure expected_record is a list
    if not isinstance(expected_record, list):
        expected_record = [expected_record]
    
    record_type = entry['record_type']

    # Run the DNS check
    result = run_dns_check(domain, expected_record, record_type)
    results.append(result)

# Write the results to a YAML file
with open('history/dns_results.yml', 'w') as outfile:
    yaml.dump(results, outfile, default_flow_style=False)

print("DNS check completed. Results written to history/dns_results.yml")
