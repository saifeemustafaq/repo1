import os
import json
import re

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

if __name__ == "__main__":
    main()
