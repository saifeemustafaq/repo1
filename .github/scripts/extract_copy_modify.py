import os
import json
import re
import shutil
import yaml
import requests

def extract_issue_details(issue_number, repo, token):
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
    }
    url = f'https://api.github.com/repos/{repo}/issues/{issue_number}'
    response = requests.get(url, headers=headers)
    issue_data = response.json()

    issue_body = issue_data.get('body', '')


    # Split the issue_body into lines
    lines = issue_body.split('\n\n')

    # Initialize variables to store the extracted values
    alias = None
    email = None
    cluster = None
    team = None

    # Loop through the lines to extract values
    for i in range(len(lines)):
        line = lines[i]
        if line.startswith('### Alias'):
            alias = lines[i+1].strip()
            print(alias)
        elif line.startswith('### Email'):
            email = lines[i+1].strip()
            print(email)
        elif line.startswith('### Cluster'):
            cluster = lines[i+1].strip()
            print(cluster)
        elif line.startswith('### Team'):
            team = lines[i+1].strip()
            print(team)

    # print("=============",alias, email, cluster, team)

    return {
        "alias": alias.strip() if alias else None,
        "email": email.strip() if email else None,
        "cluster": cluster.strip() if cluster else None,
        "team": team.strip() if team else None,
    }

def extract_field_from_body(body, field_id):
    # Regular expression pattern to match the Markdown formatted field.
    # This pattern looks for the field_id as a Markdown heading and captures the following line as the value.
    pattern = fr"### {field_id}\s*\n(.+)"
    match = re.search(pattern, body, re.MULTILINE)
    if match:
        return match.group(1).strip()  # Use strip() to remove any leading/trailing whitespace
    return None



def copy_template_directory(alias):
    source_dir = "devspaces/natarajam"
    dest_dir = f"devspaces/{alias}"
    shutil.copytree(source_dir, dest_dir)

def update_devspace_mapping(alias, email, cluster, team):
    mapping_file = "system/devspacemapping.yaml"
    with open(mapping_file) as file:
        data = yaml.safe_load(file)

    # Update the YAML structure
    data['developers'][alias] = {
        'cluster': cluster,
        'email': email,
        'labels': {'team': team}
    }

    # Write back the modified data
    with open(mapping_file, 'w') as file:
        yaml.dump(data, file)

def main():
    # Load issue and repo data from GitHub event JSON
    with open(os.environ['GITHUB_EVENT_PATH'], 'r') as file:
        event_data = json.load(file)
        issue_number = event_data['issue']['number']
        repo = os.getenv('GITHUB_REPOSITORY')  # The owner and repository name. For example, "octocat/Hello-World".
        token = os.getenv('GITHUB_TOKEN')  # This token is provided by Actions, you need to pass it to the workflow

    # Extract details
    details = extract_issue_details(issue_number, repo, token)

        # Print all the extracted details
    print(f"Extracted Issue Details:")
    for key, value in details.items():
        print(f"{key}: {value}")

    alias = details['alias']
    print(f"Debug: Alias is '{alias}'")  # Debugging statement



    # Print details for GitHub Actions to set as outputs
    for key, value in details.items():
        if value:
            print(f"::set-output name={key}::{value}")

    # Perform the file operations
    alias = details['alias']
    if alias:
        copy_template_directory(alias)
        update_devspace_mapping(alias, details['email'], details['cluster'], details['team'])

if __name__ == "__main__":
    main()
