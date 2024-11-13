import yaml        # To read the configuration file
import requests    # To make HTTP requests
import time        # To add delay between each cycle
from collections import defaultdict

def load_endpoints(file_path):
    """Load endpoints from a YAML file."""
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def check_endpoint(endpoint):
    """Sends an HTTP request to the specified endpoint and determines if it is 'UP' or 'DOWN'."""
    url = endpoint['url']
    method = endpoint.get('method', 'GET')
    headers = endpoint.get('headers', {})
    body = endpoint.get('body', None)
    
    try:
        response = requests.request(method=method, url=url, headers=headers, data=body, timeout=5)
        latency = response.elapsed.total_seconds() * 1000  # Convert to ms
        is_up = (200 <= response.status_code < 300) and (latency < 500)
        return is_up
    except requests.RequestException:
        return False

def log_availability(availability_tracker):
    """
    Calculates and logs the availability percentage for each domain.
    Rounds the result to the nearest whole percentage.
    """
    for domain, stats in availability_tracker.items():
        total_checks = stats['up'] + stats['down']
        availability = (stats['up'] / total_checks) * 100 if total_checks > 0 else 0
        print(f"{domain} has {round(availability)}% availability percentage")

def main(file_path):
    endpoints = load_endpoints(file_path)
    availability_tracker = defaultdict(lambda: {'up': 0, 'down': 0})
    
    try:
        while True:
            for endpoint in endpoints:
                url = endpoint['url']
                domain = url.split("//")[-1].split("/")[0]
                is_up = check_endpoint(endpoint)
                
                if is_up:
                    availability_tracker[domain]['up'] += 1
                else:
                    availability_tracker[domain]['down'] += 1
            
            log_availability(availability_tracker)
            time.sleep(15)
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python health_check.py <path_to_yaml_config>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    main(config_path)
