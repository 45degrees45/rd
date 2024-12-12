from flask import Flask, render_template, request, jsonify
import ollama
import os

app = Flask(__name__)

# Create templates directory
os.makedirs('templates', exist_ok=True)

# Create static directory
os.makedirs('static', exist_ok=True)

# HTML template
with open('templates/index.html', 'w') as f:
    f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>MedLlama Chat Interface</title>
    <style>
        body { 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px;
            font-family: Arial, sans-serif;
        }
        #chat-container {
            height: 400px;
            overflow-y: auto;
            border: 1px solid #ccc;
            padding: 20px;
            margin-bottom: 20px;
        }
        #input-container {
            display: flex;
            gap: 10px;
        }
        #user-input {
            flex-grow: 1;
            padding: 10px;
        }
        button {
            padding: 10px 20px;
            background-color: #007bff;
            color: white;
            border: none;
            cursor: pointer;
        }
        .message {
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 5px;
        }
        .user-message {
            background-color: #e9ecef;
        }
        .bot-message {
            background-color: #f8f9fa;
        }
    </style>
</head>
<body>
    <h1>MedLlama Chat Interface</h1>
    <div id="chat-container"></div>
    <div id="input-container">
        <input type="text" id="user-input" placeholder="Type your medical question here...">
        <button onclick="sendMessage()">Send</button>
    </div>

    <script>
        function addMessage(message, isUser) {
            const chatContainer = document.getElementById('chat-container');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
            messageDiv.textContent = `${isUser ? 'You: ' : 'MedLlama: '}${message}`;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function sendMessage() {
            const input = document.getElementById('user-input');
            const message = input.value.trim();
            
            if (message) {
                addMessage(message, true);
                input.value = '';

                fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ message: message })
                })
                .then(response => response.json())
                .then(data => {
                    addMessage(data.response, false);
                })
                .catch(error => {
                    console.error('Error:', error);
                    addMessage('Error: Could not get response', false);
                });
            }
        }

        document.getElementById('user-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
    """)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json['message']
        
        # Get response from MedLlama
        response = ollama.chat(
            model='medllama2:7b-q2_K',  # Using the smaller variant
            messages=[{
                'role': 'user',
                'content': user_message
            }]
        )
        
        return jsonify({'response': response['message']['content']})
    except Exception as e:
        return jsonify({'response': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
