import os
import json
import re
import shutil
import yaml

def extract_issue_details(issue_body):
    # Regular expressions for extracting details
    alias_regex = r"Alias\s*:\s*(.+)"
    email_regex = r"Email\s*:\s*(.+)"
    cluster_regex = r"Cluster\s*:\s*(.+)"
    team_regex = r"Team\s*:\s*(.+)"

    # Extract details using regex
    alias = re.search(alias_regex, issue_body)
    email = re.search(email_regex, issue_body)
    cluster = re.search(cluster_regex, issue_body)
    team = re.search(team_regex, issue_body)

    return {
        "alias": alias.group(1).strip() if alias else None,
        "email": email.group(1).strip() if email else None,
        "cluster": cluster.group(1).strip() if cluster else None,
        "team": team.group(1).strip() if team else None
    }

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
    # Load issue body from GitHub event JSON
    with open(os.environ['GITHUB_EVENT_PATH'], 'r') as file:
        data = json.load(file)
        issue_body = data['issue']['body']

    # Extract details
    details = extract_issue_details(issue_body)

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
