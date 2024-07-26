import requests
import os

def parse_dcf(content):
    lines = content.strip().split('\n')
    dcf_data = {}
    for line in lines:
        if line.strip(): 
            key, value = line.split(':', 1)
            dcf_data[key.strip()] = value.strip()
    return dcf_data

def fetch_release_version():
    # Fetch webpage
    url = 'https://cran.rstudio.com/src/base/VERSION-INFO.dcf'
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch webpage. Status code: {response.status_code}")
        exit(1)

    # Parse DCF content
    dcf_content = response.text
    dcf_data = parse_dcf(dcf_content)

    # Extract the value for the key 'Release'
    value = dcf_data.get('Release')
    if not value:
        print("Release information not found")
        exit(1)

    return value

if __name__ == "__main__":
    value = fetch_release_version()
    # Print the release value so it can be captured by GitHub Actions
    print(f"value={value}")
