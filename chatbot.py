import requests
import json
import pandas
import re  # Import regex module for cleaning up spaces

def chat_with_bot(prompt, history):
    try:
        full_prompt = "\n".join(history + [f"You: {prompt}", "Bot:"])
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "codestral:latest", "prompt": full_prompt}
        )
        response.raise_for_status()

        # Split concatenated JSON objects
        responses = response.text.splitlines()
        bot_responses = []

        for json_str in responses:
            try:
                json_response = json.loads(json_str)
                # Only process the "response" field if it exists
                if "response" in json_response:
                    # Strip leading and trailing spaces from the response
                    bot_responses.append(json_response["response"].strip())
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON: {e}, content: {json_str}")

        # Combine all bot responses into a single string
        combined_response = " ".join(bot_responses).strip()

        # Clean up spaces before punctuation and apostrophes
        cleaned_response = re.sub(r"\s+([.,!?'])", r"\1", combined_response)

        # Remove extra spaces between words
        cleaned_response = re.sub(r"\s{2,}", " ", cleaned_response)

        return cleaned_response.strip()
    
    except requests.exceptions.HTTPError as e:
        return f"HTTP error: {e.response.status_code} - {e.response.text}"
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"

def start_chat():
    print("Chat with Bot! Type 'exit' to end the chat.")
    conversation_history = []
    conversation_log = []

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Exiting chat. Goodbye!")
            break

        response = chat_with_bot(user_input, conversation_history)

        # Limit history to last 10 exchanges
        conversation_history.append(f"You: {user_input}")
        conversation_history.append(f"Bot: {response}")
        conversation_history = conversation_history[-20:]

        # Log conversation
        conversation_log.append({"User": user_input, "Bot": response})

        print("Bot:", response)

    # Save conversation log
    try:
        pandas.DataFrame(conversation_log).to_csv("conversation_log.csv", index=False, encoding="utf-8-sig")
        print("Conversation log saved to 'conversation_log.csv'.")
    except Exception as e:
        print(f"Failed to save conversation log: {e}")

if __name__ == "__main__":
    start_chat()
