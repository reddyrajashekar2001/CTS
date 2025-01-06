import requests
import json
import sys
import subprocess

# Define the API URL
url = "https://dm-us.informaticacloud.com/ma/api/v2/user/login"

# Get the IICS username, password, and commit hash from the input
iics_username = sys.argv[1]
iics_password = sys.argv[2]
commit_hash = sys.argv[3]

# Define the payload for IICS login
payload = json.dumps({
  "@type": "login",
  "username": iics_username,
  "password": iics_password
})

# Set headers for the request
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
}

# Send the login request
response = requests.post(url, headers=headers, data=payload)

# Check if the response is successful
if response.status_code == 200:
    data = response.json()
    user_groups = data.get('usergroups', [])
    user_name = data.get('name')
    user_email = data.get('emails')

    # Load the mapping of user groups to project folders
    with open('scripts/user_groups_mapping.json', 'r') as f:
        mapping = json.load(f)

    # Check if the user is part of the Leads group
    is_lead = any(group['name'] == 'Leads' for group in user_groups)

    # Use git show to get the affected files for the given commit hash
    try:
        git_show_output = subprocess.check_output(['git', 'show', '--name-only', '--oneline', commit_hash], stderr=subprocess.STDOUT)
        affected_files = git_show_output.decode('utf-8').splitlines()[1:]  # Skip the first line (commit hash)

        # Debugging: Print the affected files
        print(f"Affected files for commit {commit_hash}: {affected_files}")

        # Check if any of the affected files belong to the project folder under "Explore"
        project_folder = None
        for file in affected_files:
            # Check if the file is under the "Explore" folder and determine the project folder
            if file.startswith('Explore/'):
                project_folder = file.split('/')[1]  # Get the project folder name (first level under Explore)
                break

        if project_folder is None:
            print(f"No project folder found for commit {commit_hash}.")
            sys.exit(1)

        # Debugging: Print the project folder
        print(f"Project folder identified: {project_folder}")

        # Check if the user is authorized for the project folder
        if user_name in mapping.get(project_folder, []):
            if is_lead:
                print(f"User {user_name} is authorized to cherry-pick commits for {project_folder}.")
            else:
                print(f"User {user_name} is not authorized to cherry-pick commits for {project_folder}.")
                sys.exit(1)
        else:
            print(f"User {user_name} is not authorized for the project folder {project_folder}.")
            sys.exit(1)

    except subprocess.CalledProcessError as e:
        print(f"Error executing git show for commit {commit_hash}: {e.output.decode('utf-8')}")
        sys.exit(1)

else:
    print(f"Failed to authenticate user {iics_username}. Response: {response.text}")
    sys.exit(1)
