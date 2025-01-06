import requests
import json
import sys

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

    # Get the project folder from the commit hash (you will need to implement logic to map the commit hash to a folder)
    project_folder = "some_logic_to_get_project_folder_from_commit_hash"

    # Check if the user is authorized for the project folder
    if user_name in mapping.get(project_folder, []):
        if is_lead:
            print(f"User {user_name} is authorized to cherry-pick commits for {project_folder}.")
        else:
            print(f"User {user_name} is not authorized to cherry-pick commits for {project_folder}.")
            sys.exit(1)
    else:
        print(f"User {user_name} is not authorized for this project folder.")
        sys.exit(1)

else:
    print(f"Failed to authenticate user {iics_username}. Response: {response.text}")
    sys.exit(1)
