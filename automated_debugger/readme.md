# Ollama Debug Runner

An interactive debugging tool that uses Ollama's Qwen model to automatically fix Python code errors. This tool provides a user-friendly interface with colored output, explanations of fixes, and code diffs.

## Features

- 🤖 Automated code fixing using Ollama's Qwen model
- 🎨 Colored output for better readability
- 📊 Side-by-side code diff visualization
- 💡 Explanations of detected issues and proposed fixes
- 📝 Automatic backup creation before applying fixes
- ⏱️ Execution timeout protection
- 🔄 Interactive debugging loop with multiple attempt support

## Prerequisites

- Python 3.6+
- Ollama installed with Qwen2.5-coder model
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ollama-debug-runner.git
cd ollama-debug-runner
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Ensure Ollama is installed and the Qwen model is available:
```bash
ollama list  # Should show qwen2.5-coder:0.5b
```

## Usage

1. Basic usage:
```bash
python ollama-debug-runner.py your_code.py
```

2. The tool will:
   - Run your code and detect errors
   - Generate fixes using Ollama
   - Show colored diffs of proposed changes
   - Create backups before applying fixes
   - Provide explanations of the issues

## Example

```python
# Sample broken code in test.py
def greet(name)    # Missing colon
    print("Hello, " + name)

greet("World")
```

Run the debugger:
```bash
python ollama-debug-runner.py test.py
```

## Configuration

The debug runner can be configured by modifying the following parameters in the `OllamaDebugRunner` class:

- `model_name`: The Ollama model to use (default: "qwen2.5-coder:0.5b")
- `temperature`: Model temperature (default: 0.1)
- `max_attempts`: Maximum debug attempts (default: 5)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to Ollama for providing the local AI model infrastructure
- Thanks to the Qwen team for the coding-optimized model
