import requests
import json
import numpy  # Added numpy
import pandas  # Added pandas

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

# Chat loop with conversation logging
def start_chat():
    print("Chat with Bot! Type 'exit' to end the chat.")
    conversation_history = []  # List to store the conversation history
    conversation_log = pandas.DataFrame(columns=["User", "Bot"])  # DataFrame to log conversations
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Exiting chat. Goodbye!")
            break
        
        # Get the response from Bot
        response = chat_with_bot(user_input, conversation_history)
        
        # Log the conversation
        conversation_history.append(f"You: {user_input}")
        conversation_history.append(f"Bot: {response}")
        conversation_log = pandas.concat([conversation_log, pandas.DataFrame({"User": [user_input], "Bot": [response]})], ignore_index=True)
        
        # Print the response
        print("Bot:", response)
    
    # Save the conversation log to a CSV file
    try:
        conversation_log.to_csv("conversation_log.csv", index=False, mode="w", encoding="utf-8-sig")
        print("Conversation log saved to 'conversation_log.csv'.")
    except Exception as e:
        print(f"Failed to save conversation log: {e}")

# Start the chat
if __name__ == "__main__":
    start_chat()