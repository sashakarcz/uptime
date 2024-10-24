import json
import subprocess
import yaml
import os

# Load domains from YAML file
def load_domains(yaml_file):
    with open(yaml_file, 'r') as file:
        try:
            domains = yaml.safe_load(file)
            return domains['domains']
        except yaml.YAMLError as e:
            print(f"Error loading YAML file: {e}")
            return []

# Perform DNS check using dig
def dns_check(domain, record_type):
    try:
        # Use subprocess to run the dig command and capture the output
        result = subprocess.check_output(
            ['dig', '+short', domain, record_type],
            universal_newlines=True
        ).strip()
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error performing DNS check for {domain}: {e}")
        return "ERROR: DNS check failed"

# Append results to dns_results.json
def append_results(json_file, domain, expected, actual):
    if not os.path.exists(json_file):
        with open(json_file, 'w') as file:
            json.dump([], file)

    with open(json_file, 'r') as file:
        data = json.load(file)

    data.append({
        "domain": domain,
        "expected": expected,
        "actual": actual
    })

    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)

def main():
    domains = load_domains('config/domains.yml')
    
    # Initialize JSON file if it doesn't exist
    if not os.path.exists('dns_results.json'):
        with open('dns_results.json', 'w') as f:
            json.dump([], f)

    for entry in domains:
        domain = entry['domain']
        expected_record = entry['expected_record']
        record_type = entry['record_type']

        print(f"Running DNS check for {domain} (Type: {record_type}, Expected: {expected_record})")
        actual_record = dns_check(domain, record_type)

        print(f"Result for {domain}: {actual_record}")

        append_results('dns_results.json', domain, expected_record, actual_record)

if __name__ == "__main__":
    main()

