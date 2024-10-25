import yaml
import subprocess
from datetime import datetime

# Load the config/domains.yml file
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
        else:
            # Split the result into a list if there are multiple entries
            result = result.splitlines()

        # Compare the result with the expected record
        if expected_record in result:
            print(f"DNS check passed for {domain}")
        else:
            print(f"DNS check failed for {domain}. Got {result}, expected {expected_record}")

        return {"domain": domain, "expected": expected_record, "actual": result, "timestamp": str(datetime.utcnow())}

    except subprocess.CalledProcessError as e:
        print(f"Error during DNS check for {domain}: {str(e)}")
        return {"domain": domain, "expected": expected_record, "actual": "Error", "timestamp": str(datetime.utcnow())}

# Iterate over the DNS entries in config/domains.yml
for entry in config['domains']:
    domain = entry['domain']
    expected_record = entry['expected_record']
    record_type = entry['record_type']

    # Run the DNS check
    result = run_dns_check(domain, expected_record, record_type)
    results.append(result)

# Write the results to a YAML file
with open('history/dns_results.yaml', 'w') as outfile:
    yaml.dump(results, outfile, default_flow_style=False)

print("DNS check completed. Results written to history/dns_results.yaml")
