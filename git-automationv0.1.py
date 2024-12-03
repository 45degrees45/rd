import subprocess
import os
import logging
from getpass import getpass

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_command(command, description):
    logging.info(f"Executing: {description}")
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        logging.info(f"Success: {description}")
        return result
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed: {description}")
        logging.error(f"Error message: {e.stderr}")
        raise

def git_automate(repo_url, username, password):
    logging.info("Starting Git automation process")
    
    # Initialize repo if needed
    if not os.path.exists('.git'):
        logging.info("Git repository not found, initializing...")
        run_command(['git', 'init'], "Git init")
    else:
        logging.info("Git repository already exists")
        
    # Configure credentials
    logging.info("Configuring Git credentials")
    credential_helper = f'!f() {{ echo "username={username}"; echo "password={password}"; }};f'
    run_command(['git', 'config', '--local', 'credential.helper', credential_helper], 
                "Setting credentials")
    
    # Add remote if not exists
    try:
        logging.info("Adding remote origin")
        run_command(['git', 'remote', 'add', 'origin', repo_url], 
                   "Adding remote repository")
    except subprocess.CalledProcessError:
        logging.warning("Remote 'origin' already exists, continuing...")
        
    # Check current status
    status = run_command(['git', 'status'], "Checking Git status")
    logging.info(f"Current status:\n{status.stdout}")
    
    # Stage changes
    logging.info("Staging all changes")
    run_command(['git', 'add', '.'], "Git add")
    
    # Commit
    logging.info("Committing changes")
    run_command(['git', 'commit', '-m', 'Auto commit'], "Git commit")
    
    # Push
    logging.info("Pushing to remote repository")
    run_command(['git', 'push', '-u', 'origin', 'main'], "Git push")
    
    logging.info("Git automation completed successfully")

if __name__ == "__main__":
    logging.info("Starting script")
    repo_url = input("Enter repository URL: ")
    username = input("Enter Git username: ")
    password = getpass("Enter Git password/token: ")
    
    try:
        git_automate(repo_url, username, password)
    except Exception as e:
        logging.error(f"Script failed: {str(e)}")
        raise
