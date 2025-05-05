import json
import requests

def call_llm(prompt, endpoint="http://localhost:1234/v1/chat/completions"):
    """
    Sends a prompt to the local LLM endpoint and returns the response text.
    Implement this using the 'requests' library and the specific API format
    expected by your LM Studio setup for the Gemma model.
    """
    print(f"--- Calling LLM ---")
    # Placeholder implementation - replace with actual API call
    headers = {"Content-Type": "application/json"}
    # Consult LM Studio documentation for the correct payload structure
    payload = json.dumps({
      "model": "gemma-3-1b-it", 
      "messages": [
        {"role": "system", "content": "You are an AI assistant evaluating course content."},
        {"role": "user", "content": prompt}
      ],
      "temperature": 0.7, # Adjust as needed
      "max_tokens": 500 # Adjust as needed
    })

    try:
        response = requests.post(endpoint, headers=headers, data=payload) # Uncomment locally
        response.raise_for_status() 
        llm_response = response.json()
        # Extract the actual text response based on LM Studio's output format
        # This might be nested, e.g., llm_response['choices'][0]['message']['content']
        result_text = llm_response['choices'][0]['message']['content'].strip() # EXAMPLE PARSING
   
        return result_text
    except Exception as e: # Replace 'Exception' with specific exceptions like requests.exceptions.RequestException locally
        print(f"Error calling LLM: {e}")
        return None
