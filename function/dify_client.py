# dify_client.py
import requests
import json
import traceback

class DifyClient:
    def __init__(self, api_base_url, api_key, user_id="generic_user"): # Changed default user_id
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.user_id = user_id

    def chat_stream(self, user_input, current_conversation_id):
        """
        Calls the Dify chat flow API.
        Yields streamed response parts, metadata (like conversation_id), or error dictionaries.
        Raises exceptions for critical request failures.
        """
        url = f"{self.api_base_url}/chat-messages"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "inputs": {}, 
            "query": user_input,
            "user": self.user_id,
            "response_mode": "streaming",
            "auto_generate_name": False
        }

        if current_conversation_id:
            payload["conversation_id"] = current_conversation_id
        
        # Print statements are for server-side logging/debugging if needed.
        # print(f"DifyClient: Sending request to {url}")
        # print(f"DifyClient: Payload: {json.dumps(payload, indent=2)}")

        try:
            response = requests.post(url, json=payload, headers=headers, stream=True, timeout=600)
            # print(f"DifyClient: Response status code: {response.status_code}")
            response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)

            for chunk in response.iter_lines():
                if chunk:
                    decoded_chunk = chunk.decode('utf-8')
                    # print(f"DifyClient: Raw chunk: {decoded_chunk}") 
                    if decoded_chunk.startswith("data:"):
                        if decoded_chunk.strip() == "data:":
                            # This is often a keep-alive ping, skip it.
                            continue
                        
                        data_str = decoded_chunk[len("data: "):]
                        try:
                            data = json.loads(data_str)
                            # print(f"DifyClient: Parsed data: {data}")

                            if "conversation_id" in data:
                                # Yield metadata separately
                                yield {"type": "metadata", "conversation_id": data["conversation_id"]}
                            
                            if "answer" in data and data["answer"] is not None:
                                yield data["answer"] # Yield content as string
                            
                            if data.get("event") == "error":
                                error_message_dify = data.get('message', 'Unknown Dify error event')
                                print(f"DIFY API Error Event (from client): {data}") 
                                yield {"type": "error", "source": "dify_event", "message": error_message_dify, "details": data}
                                return # Stop further processing on Dify error event

                            if data.get("event") in ["workflow_finished", "message_end"]:
                                # If conversation_id is only available at the end, it would have been caught by the check above.
                                # message_end might contain the full answer if not streamed progressively.
                                # However, we assume "answer" field in intermediate chunks is the primary source for streaming.
                                if data.get("event") == "message_end" and "answer" in data and data["answer"] is not None:
                                    # This could be redundant if answer chunks were already sent.
                                    # For now, we prioritize yielding "answer" when it appears.
                                    # If your Dify app only sends the full answer at message_end, you might need to adjust.
                                    pass 
                                # print(f"DifyClient: Event {data.get('event')}")


                        except json.JSONDecodeError:
                            print(f"Warning (from DifyClient): Could not decode JSON from data chunk: {data_str}")
                            # Optionally yield a client-side error here if needed by the UI
                            # yield {"type": "error", "source": "client_json_decode", "message": "Failed to decode server data."}
                        except Exception as e: # Catch other errors during data processing
                            print(f"Error (from DifyClient) processing Dify data chunk: {data_str if 'data_str' in locals() else decoded_chunk}, Error: {e}")
                            traceback.print_exc()
                            # yield {"type": "error", "source": "client_processing", "message": str(e)}


        except requests.exceptions.HTTPError as e:
            # Let HTTP errors propagate to be caught by the caller
            print(f"HTTP Error (from DifyClient): {e.response.status_code}, Response: {e.response.text}")
            raise  # Re-raise the exception
        except requests.exceptions.RequestException as e:
            # Let other request-related errors propagate
            print(f"Request Error (from DifyClient): {e}")
            raise  # Re-raise the exception
        except Exception as e:
            # Catch any other unexpected errors in the client
            print(f"An unexpected error occurred in DifyClient: {e}")
            traceback.print_exc()
            # yield {"type": "error", "source": "client_unexpected", "message": "An unexpected error occurred in the Dify client."}
            # Or re-raise if the caller should handle absolutely everything:
            raise