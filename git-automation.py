import subprocess
import os
import logging
import sys
from getpass import getpass
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('git_automation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Default values
DEFAULT_REPO = "https://github.com/45degrees45/rd"
DEFAULT_USERNAME = "tcjosep@gmail.com"
DEFAULT_BRANCH = "main"

# Files to ignore for security
SENSITIVE_PATTERNS = [
    '.env',
    'config.ini',
    'secrets.yaml',
    '**/auth.*',
    '**/credentials.*'
]

def run_command(command, description, retry_count=3):
    for attempt in range(retry_count):
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            logging.info(f"Success: {description}")
            return result
        except subprocess.CalledProcessError as e:
            if "Repository rule violations found" in str(e.stderr):
                logging.error("Security violation detected. Please check .gitignore and remove sensitive files.")
                raise
            if attempt < retry_count - 1:
                logging.warning(f"Attempt {attempt + 1} failed for {description}: {e.stderr}")
                continue
            logging.error(f"Error in {description}: {e.stderr}")
            raise

def ensure_gitignore():
    """Ensure .gitignore exists and contains necessary patterns"""
    if not os.path.exists('.gitignore'):
        with open('.gitignore', 'w') as f:
            for pattern in SENSITIVE_PATTERNS:
                f.write(f"{pattern}\n")
    else:
        with open('.gitignore', 'r') as f:
            current_content = f.read()
        with open('.gitignore', 'a') as f:
            for pattern in SENSITIVE_PATTERNS:
                if pattern not in current_content:
                    f.write(f"{pattern}\n")

def remove_sensitive_files_from_tracking():
    """Remove sensitive files from git tracking while keeping them locally"""
    for pattern in SENSITIVE_PATTERNS:
        try:
            subprocess.run(['git', 'rm', '--cached', '-r', pattern], 
                         capture_output=True, text=True, check=False)
        except subprocess.CalledProcessError:
            pass  # Ignore errors if files don't exist

def git_automate(repo_url=DEFAULT_REPO, username=DEFAULT_USERNAME, password=None):
    try:
        # Get or prompt for password
        if not password:
            password = getpass("Enter Git password/token: ")

        # Ensure .gitignore is properly set up
        ensure_gitignore()
        
        # Remove sensitive files from tracking
        remove_sensitive_files_from_tracking()

        # Get current branch
        current_branch = run_command(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            "Getting current branch"
        ).stdout.strip()

        # Configure credentials
        credential_helper = f'!f() {{ echo "username={username}"; echo "password={password}"; }};f'
        run_command(['git', 'config', '--local', 'credential.helper', credential_helper],
                   "Setting credentials")

        # Check if there are any changes to commit
        status = run_command(['git', 'status', '--porcelain'], "Checking git status")
        if status.stdout.strip():
            # Pull latest changes first
            run_command(['git', 'pull', 'origin', current_branch], "Pulling latest changes")
            
            # Stage and commit changes
            run_command(['git', 'add', '.'], "Staging changes")
            commit_message = f'Auto commit - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            run_command(['git', 'commit', '-m', commit_message], "Committing")
            run_command(['git', 'push', 'origin', current_branch], "Pushing changes")
            logging.info("Successfully pushed changes to repository")
        else:
            logging.info("No changes to commit")

        return True

    except Exception as e:
        logging.error(f"Git automation failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = git_automate()
    if not success:
        sys.exit(1)