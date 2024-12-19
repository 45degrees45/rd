import sys
import subprocess
import time
from pathlib import Path
import ollama
import json
from colorama import init, Fore, Back, Style
from difflib import unified_diff

# Initialize colorama for cross-platform color support
init()

class OllamaDebugRunner:
    def __init__(self, model_name="qwen2.5-coder:0.5b", temperature=0.1):
        self.model_name = model_name
        self.model_config = {
            'temperature': temperature,
            'num_predict': 512,
            'top_k': 10,
            'top_p': 0.9,
        }
        
    def run_code(self, file_path):
        """Run Python file and return any errors"""
        try:
            result = subprocess.run(
                [sys.executable, file_path],
                capture_output=True,
                text=True,
                timeout=30
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
        relevant_lines = []
        for line in lines:
            if any(key in line.lower() for key in ['error:', 'exception:', 'traceback']):
                relevant_lines.append(line)
        return '\n'.join(relevant_lines)

    def get_ai_suggestion(self, code, error):
        """Get code fix suggestion from Ollama"""
        prompt = f"""You are an expert Python debugger. Analyze and fix this code that produced the following error:

ERROR:
{error}

CODE:
{code}

Provide your response in the following format:
EXPLANATION: Brief explanation of what's wrong and how to fix it
CODE: The corrected code (only pure Python, no markdown)"""
        
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{
                    'role': 'system',
                    'content': 'You are an expert Python debugger. Provide clear explanations and working code fixes.'
                }, {
                    'role': 'user',
                    'content': prompt
                }],
                options=self.model_config
            )
            
            content = response['message']['content']
            # Split explanation and code
            parts = content.split('CODE:')
            if len(parts) > 1:
                explanation = parts[0].replace('EXPLANATION:', '').strip()
                code = parts[1].strip()
            else:
                explanation = "No explanation provided"
                code = content
                
            return explanation, self._clean_code(code)
        except Exception as e:
            print(f"{Fore.RED}Error getting AI suggestion: {e}{Style.RESET_ALL}")
            return None, None

    def _clean_code(self, response):
        """Clean and validate the code response"""
        code = response.replace('```python', '').replace('```', '')
        lines = code.split('\n')
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
            
        cleaned_lines = []
        for line in lines:
            cleaned_line = line.replace('\t', '    ')
            cleaned_lines.append(cleaned_line)
            
        return '\n'.join(cleaned_lines)

    def show_diff(self, old_code, new_code):
        """Show colored diff between old and new code"""
        old_lines = old_code.splitlines(keepends=True)
        new_lines = new_code.splitlines(keepends=True)
        
        print(f"\n{Fore.CYAN}📋 Code Changes:{Style.RESET_ALL}")
        print("─" * 50)
        
        for line in unified_diff(old_lines, new_lines, fromfile='Before', tofile='After', lineterm=''):
            if line.startswith('+') and not line.startswith('+++'):
                print(f"{Fore.GREEN}{line.rstrip()}{Style.RESET_ALL}")
            elif line.startswith('-') and not line.startswith('---'):
                print(f"{Fore.RED}{line.rstrip()}{Style.RESET_ALL}")
            else:
                print(line.rstrip())
        
        print("─" * 50)

    def update_file(self, file_path, new_code):
        """Update the file with new code and create a backup"""
        backup_path = f"{file_path}.backup"
        try:
            with open(file_path, 'r') as src, open(backup_path, 'w') as dst:
                dst.write(src.read())
            print(f"{Fore.GREEN}✓ Backup created: {backup_path}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ Warning: Could not create backup: {e}{Style.RESET_ALL}")

        with open(file_path, 'w') as f:
            f.write(new_code)

    def run_debug_loop(self, file_path):
        """Main debugging loop"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"{Fore.RED}Error: File {file_path} not found{Style.RESET_ALL}")
            return

        max_attempts = 5
        attempt = 0
        
        print(f"\n{Fore.CYAN}🔍 Starting Debug Session for: {file_path}{Style.RESET_ALL}")
        print("=" * 60)
        
        while attempt < max_attempts:
            attempt += 1
            print(f"\n{Fore.YELLOW}📌 Debug Attempt {attempt}/{max_attempts}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}▶ Running code...{Style.RESET_ALL}")
            
            error = self.run_code(file_path)
            
            if not error:
                print(f"\n{Fore.GREEN}✨ Success! Code ran without errors!{Style.RESET_ALL}")
                break
                
            print(f"\n{Fore.RED}❌ Error Detected:{Style.RESET_ALL}")
            print(f"{Fore.RED}{error}{Style.RESET_ALL}")
            
            with open(file_path) as f:
                current_code = f.read()
            
            print(f"\n{Fore.CYAN}🤖 Analyzing code and generating fix...{Style.RESET_ALL}")
            explanation, suggestion = self.get_ai_suggestion(current_code, error)
            
            if not suggestion:
                print(f"\n{Fore.YELLOW}⚠ Failed to get AI suggestion. Options:{Style.RESET_ALL}")
                print("1. Try again")
                print("2. Enter code manually")
                print("3. Restore from backup")
                print("4. Exit")
                choice = input(f"{Fore.CYAN}Enter choice (1-4): {Style.RESET_ALL}")
                
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
                        print(f"{Fore.RED}No backup file found{Style.RESET_ALL}")
                        continue
                else:
                    break
            
            if explanation:
                print(f"\n{Fore.CYAN}💡 Analysis:{Style.RESET_ALL}")
                print(f"{Fore.WHITE}{explanation}{Style.RESET_ALL}")
            
            self.show_diff(current_code, suggestion)
            
            apply = input(f"\n{Fore.CYAN}Apply this fix? (y/n): {Style.RESET_ALL}").lower()
            if apply == 'y':
                self.update_file(file_path, suggestion)
                print(f"{Fore.GREEN}✓ Fix applied successfully!{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.YELLOW}⚠ Fix skipped{Style.RESET_ALL}")
                choice = input(f"{Fore.CYAN}Continue debugging? (y/n): {Style.RESET_ALL}").lower()
                if choice != 'y':
                    break

def main():
    if len(sys.argv) != 2:
        print(f"{Fore.RED}Usage: python ollama_debug_runner.py <python_file>{Style.RESET_ALL}")
        sys.exit(1)
        
    runner = OllamaDebugRunner()
    runner.run_debug_loop(sys.argv[1])

if __name__ == "__main__":
    main()
