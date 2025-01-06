name: Cherry Pick Commit on GitHub-Hosted Windows

on:
  workflow_dispatch:
    inputs:
      from_branch:
        description: "Branch to cherry-pick from (source branch)"
        required: true
        type: string
      to_branch:
        description: "Branch to cherry-pick to (target branch)"
        required: true
        type: string
      commit_hash:
        description: "6-digit commit hash to cherry-pick"
        required: true
        type: string
      iics_username:
        description: "IICS username for login"
        required: true
        type: string
      iics_password:
        description: "IICS password for login"
        required: true
        type: string

permissions:
  contents: write  # Ensure permissions to push changes

jobs:
  cherry-pick:
    runs-on: windows-latest  # Use GitHub-hosted Windows runner

    steps:
      # Step 1: Checkout the target branch (where the cherry-pick will be applied)
      - name: Checkout Target Branch
        uses: actions/checkout@v4
        with:
          ref: ${{ inputs.to_branch }}
          fetch-depth: 0  # Fetch full history for cherry-pick

      # Step 2: Checkout the default branch (scripts folder) to access the scripts
      - name: Checkout Default Branch (Scripts Folder)
        uses: actions/checkout@v4
        with:
          ref: main  # or your default branch
          path: scripts  # Checkout only the scripts folder to a specific directory

      # Step 3: List the files in the repository (for debugging)
      - name: List files in the repository
        run: dir

      # Step 4: Install Python
      - name: Install Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'

      # Step 5: Install Requirements for the scripts
      - name: Install Requirements
        run: pip install -r scripts/requirements.txt

      # Step 6: Run IICS Login and Validation
      - name: Run IICS Login and Validation
        run: |
          python scripts/iics_login_and_validate.py ${{ inputs.iics_username }} ${{ inputs.iics_password }} ${{ inputs.commit_hash }}
        env:
          IICS_USERNAME: ${{ secrets.IICS_USERNAME }}
          IICS_PASSWORD: ${{ secrets.IICS_PASSWORD }}

      # Step 7: Configure Git User
      - name: Configure Git User
        if: success()
        run: |
          git config --global user.name "${{ env.GIT_USERNAME }}"
          git config --global user.email "${{ env.GIT_EMAIL }}"

      # Step 8: Fetch the source branch from which the cherry-pick is to be made
      - name: Fetch Source Branch
        run: |
          git fetch origin ${{ inputs.from_branch }}:${{ inputs.from_branch }}

      # Step 9: Cherry-pick the commit from the source branch to the target branch
      - name: Cherry-pick Commit with Recursive Strategy and -X theirs
        run: |
          git cherry-pick --strategy=recursive -X theirs ${{ inputs.commit_hash }}

      # Step 10: Temporarily ignore the 'scripts' folder before pushing to remote
      - name: Temporarily Ignore Scripts Folder
        run: |
          echo "scripts/" >> .gitignore

      # Step 11: Push changes to the remote repository
      - name: Push Changes to Remote
        run: |
          git add .
          git commit -m "Cherry-pick commit ${{ inputs.commit_hash }} from ${{ inputs.from_branch }}"
          git push origin ${{ inputs.to_branch }}

      # Step 12: Remove the 'scripts' folder from .gitignore after pushing (if needed)
      - name: Remove Scripts Folder from .gitignore
        run: |
          sed -i '/scripts\//d' .gitignore
          git add .gitignore
          git commit -m "Remove scripts folder from .gitignore"
          git push origin ${{ inputs.to_branch }}
