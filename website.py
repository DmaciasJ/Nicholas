from flask import Flask, request, jsonify, render_template
import requests
import json
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Initialize conversation history and log
conversation_history = []
conversation_log = pd.DataFrame(columns=["Timestamp", "Speaker", "Message"])

def chat_with_bot(prompt, history):
    try:
        # Combine the conversation history with the current prompt
        full_prompt = "\n".join(history + [f"You: {prompt}", "Bot:"])
        
        response = requests.post(
            "http://localhost:11434/api/generate",  # Ollama's local API endpoint
            json={"model": "llama3.1", "prompt": full_prompt},
            stream=True  # Enable streaming response
        )
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        
        # Process the streamed response
        full_response = ""
        for line in response.iter_lines():
            if line:  # Ignore empty lines
                try:
                    json_line = json.loads(line.decode("utf-8"))  # Parse each line as JSON
                    if "response" in json_line:
                        full_response += json_line["response"]
                    if json_line.get("done", False):  # Stop if "done" is true
                        break
                except json.JSONDecodeError:
                    return f"Invalid JSON in stream: {line.decode('utf-8')}"
        
        return full_response if full_response else "No response received."
    
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"

@app.route("/")
def index():
    """Render the chatbot interface."""
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """Handle user input and return bot response."""
    global conversation_history, conversation_log
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"response": "Please enter a message."})
    
    # Get the bot response
    response = chat_with_bot(user_input, conversation_history)
    
    # Log the conversation with timestamps
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conversation_history.append(f"You: {user_input}")
    conversation_history.append(f"Bot: {response}")
    conversation_log = pd.concat([
        conversation_log,
        pd.DataFrame([
            {"Timestamp": timestamp, "Speaker": "User", "Message": user_input},
            {"Timestamp": timestamp, "Speaker": "Bot", "Message": response}
        ])
    ], ignore_index=True)
    
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)