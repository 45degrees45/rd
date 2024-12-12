import subprocess
import os
import logging
from getpass import getpass

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_command(command, description):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        logging.info(f"Success: {description}")
        return result
    except subprocess.CalledProcessError as e:
        logging.error(f"Error in {description}: {e.stderr}")
        raise

def git_automate(repo_url, username, password):
    # Get current branch
    current_branch = run_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                               "Getting current branch").stdout.strip()
    
    # Configure credentials
    credential_helper = f'!f() {{ echo "username={username}"; echo "password={password}"; }};f'
    run_command(['git', 'config', '--local', 'credential.helper', credential_helper], 
                "Setting credentials")
    
    # Pull latest changes
    run_command(['git', 'pull', 'origin', current_branch], "Pulling latest changes")
    
    # Stage and push
    run_command(['git', 'add', '.'], "Staging changes")
    run_command(['git', 'commit', '-m', 'Auto commit'], "Committing")
    run_command(['git', 'push', 'origin', current_branch], "Pushing changes")

if __name__ == "__main__":
    repo_url = input("Enter repository URL: ")
    username = input("Enter Git username: ")
    password = getpass("Enter Git password/token: ")
    
    try:
        git_automate(repo_url, username, password)
    except Exception as e:
        logging.error(f"Script failed: {str(e)}")
        raise
