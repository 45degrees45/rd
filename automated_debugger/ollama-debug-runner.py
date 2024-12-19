import sys
import subprocess
import time
from pathlib import Path
import ollama
import json

class OllamaDebugRunner:
    def __init__(self, model_name="qwen2.5-coder:0.5b", temperature=0.1):
        self.model_name = model_name
        self.model_config = {
            'temperature': temperature,  # Lower temperature for more focused code fixes
            'num_predict': 512,         # Reasonable limit for code responses
            'top_k': 10,               # Reduced for more precise responses
            'top_p': 0.9,              # Slightly reduced for better focus
        }
        
    def run_code(self, file_path):
        """Run Python file and return any errors"""
        try:
            result = subprocess.run(
                [sys.executable, file_path],
                capture_output=True,
                text=True,
                timeout=30  # Add timeout to prevent hanging
            )
            if result.returncode != 0:
                return self._format_error(result.stderr)
            return None
        except subprocess.TimeoutExpired:
            return "Error: Code execution timed out after 30 seconds"
        except Exception as e:
            return str(e)

    def _format_error(self, error):
        """Format error message to be more suitable for the model"""
        lines = error.split('\n')
        # Keep only the most relevant parts of the error
        relevant_lines = []
        for line in lines:
            if any(key in line.lower() for key in ['error:', 'exception:', 'traceback']):
                relevant_lines.append(line)
        return '\n'.join(relevant_lines)

    def get_ai_suggestion(self, code, error):
        """Get code fix suggestion from Ollama"""
        prompt = f"""You are an expert Python debugger. Fix this code that produced the following error:

ERROR:
{error}

CODE:
{code}

Provide ONLY the corrected code without any explanations or markdown formatting.
The response should be pure Python code that can be executed directly."""
        
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{
                    'role': 'system',
                    'content': 'You are an expert Python debugger. Provide only working code without explanations.'
                }, {
                    'role': 'user',
                    'content': prompt
                }],
                options=self.model_config
            )
            return self._clean_code(response['message']['content'])
        except Exception as e:
            print(f"Error getting AI suggestion: {e}")
            return None

    def _clean_code(self, response):
        """Clean and validate the code response"""
        # Remove any markdown code blocks
        code = response.replace('```python', '').replace('```', '')
        
        # Remove leading/trailing whitespace while preserving indentation
        lines = code.split('\n')
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
            
        # Ensure consistent indentation (using spaces)
        cleaned_lines = []
        for line in lines:
            # Replace tabs with spaces
            cleaned_line = line.replace('\t', '    ')
            cleaned_lines.append(cleaned_line)
            
        return '\n'.join(cleaned_lines)

    def update_file(self, file_path, new_code):
        """Update the file with new code and create a backup"""
        # Create backup
        backup_path = f"{file_path}.backup"
        try:
            with open(file_path, 'r') as src, open(backup_path, 'w') as dst:
                dst.write(src.read())
            print(f"Backup created: {backup_path}")
        except Exception as e:
            print(f"Warning: Could not create backup: {e}")

        # Update file
        with open(file_path, 'w') as f:
            f.write(new_code)

    def run_debug_loop(self, file_path):
        """Main debugging loop"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"Error: File {file_path} not found")
            return

        max_attempts = 5
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            print(f"\nDebug attempt {attempt}/{max_attempts}")
            print(f"Running {file_path}...")
            
            error = self.run_code(file_path)
            
            if not error:
                print("✅ Code ran successfully!")
                break
                
            print(f"\n❌ Error encountered:\n{error}")
            
            with open(file_path) as f:
                current_code = f.read()
            
            print("\n🤖 Getting AI suggestion...")
            suggestion = self.get_ai_suggestion(current_code, error)
            
            if not suggestion:
                print("\nFailed to get AI suggestion. Options:")
                print("1. Try again")
                print("2. Enter code manually")
                print("3. Restore from backup")
                print("4. Exit")
                choice = input("Enter choice (1-4): ")
                
                if choice == '1':
                    continue
                elif choice == '2':
                    print("\nEnter new code (Ctrl+D or Ctrl+Z when done):")
                    suggestion = sys.stdin.read()
                elif choice == '3':
                    backup_path = f"{file_path}.backup"
                    if Path(backup_path).exists():
                        with open(backup_path) as f:
                            suggestion = f.read()
                    else:
                        print("No backup file found")
                        continue
                else:
                    break
            
            print("\nSuggested fix:")
            print("=" * 40)
            print(suggestion)
            print("=" * 40)
            
            apply = input("\nApply this fix? (y/n): ").lower()
            if apply == 'y':
                self.update_file(file_path, suggestion)
            else:
                print("\nSkipping this suggestion.")
                choice = input("Continue debugging? (y/n): ").lower()
                if choice != 'y':
                    break

def main():
    if len(sys.argv) != 2:
        print("Usage: python ollama_debug_runner.py <python_file>")
        sys.exit(1)
        
    runner = OllamaDebugRunner()
    runner.run_debug_loop(sys.argv[1])

if __name__ == "__main__":
    main()
