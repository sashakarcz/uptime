import yaml
import subprocess
import json
from datetime import datetime

# Load the .upptimerc.yml file
with open('config/domains.yml', 'r') as file:
    config = yaml.safe_load(file)

# Initialize the results array
results = []

# Function to run a DNS check
def run_dns_check(domain, expected_record, record_type):
    print(f"Running DNS check for {domain} (Type: {record_type}, Expected: {expected_record})")
    try:
        # Run the dig command to get the DNS record
        result = subprocess.check_output(["dig", "+short", domain, record_type], text=True).strip()

        if not result:
            result = "No record found"

        # Compare the result with the expected record
        if result == expected_record:
            print(f"DNS check passed for {domain}")
        else:
            print(f"DNS check failed for {domain}. Got {result}, expected {expected_record}")

        return {"domain": domain, "expected": expected_record, "actual": result, "timestamp": str(datetime.utcnow())}

    except subprocess.CalledProcessError as e:
        print(f"Error during DNS check for {domain}: {str(e)}")
        return {"domain": domain, "expected": expected_record, "actual": "Error", "timestamp": str(datetime.utcnow())}

# Iterate over the sites and check for DNS checks
for site in config['sites']:
    if 'check' in site and site['check'] == 'dns':
        domain = site['domain']
        expected_record = site['expected_record']
        record_type = site['record_type']

        # Run the DNS check
        result = run_dns_check(domain, expected_record, record_type)
        results.append(result)

# Write the results to a JSON file
with open('history/dns_results.json', 'w') as outfile:
    json.dump(results, outfile, indent=4)

print("DNS check completed. Results written to dns_results.json")
