import requests
import yaml
import os

input_file_path = 'input.yaml'
template_file_path = 'template.yaml'

if os.path.exists(input_file_path):
    with open(input_file_path, 'r') as file:
        yaml_data = yaml.safe_load(file)
else:
    yaml_data = {}

if 'rbase' not in yaml_data:
    if os.path.exists(template_file_path):
        with open(template_file_path, 'r') as file:
            template_data = yaml.safe_load(file)
            if 'rbase' in template_data:
                yaml_data['rbase'] = template_data['rbase']

# Function to parse DCF content
def parse_dcf(content):
    lines = content.strip().split('\n')
    dcf_data = {}
    for line in lines:
        if line.strip(): 
            key, value = line.split(':', 1)
            dcf_data[key.strip()] = value.strip()
    return dcf_data

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
release_value = dcf_data.get('Release')
if not release_value:
    print("Release information not found")
    exit(1)

# Function to update values in the input file
def update_new_value(data, keys, value):
    if len(keys) == 1:
        data[keys[0]] = value
    else:
        if keys[0] not in data:
            data[keys[0]] = {}
        update_new_value(data[keys[0]], keys[1:], value)
        
update_new_value(yaml_data, ['rbase', 'Env', 'R'], release_value)  
update_new_value(yaml_data, ['rbase', 'Build_layer_tag'], "r-"+ release_value +"v0-dev")  


# Writing updated data to input file
with open(input_file_path, 'w') as file:
    yaml.dump(yaml_data, file, default_flow_style=False)
