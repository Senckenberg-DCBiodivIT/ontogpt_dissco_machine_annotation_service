import time
import requests
import subprocess
import websocket
import json
import logging
import threading

template_path = "src/ontogpt/templates/biodiversity_with_prompt_v2.yaml"
websocket_url = "ws://0.0.0.0:8000/ws/new_message"
processed_message_url = "http://0.0.0.0:8000/processed_message"
error_message_url = "http://0.0.0.0:8000/error_message"

logging.basicConfig(level=logging.INFO)

def process_input_text(input_text):
    try:
        process = subprocess.run(
            ['ontogpt', '-v', 'extract', '-t', template_path, '-m', 'ollama/llama3'],
            input=input_text,
            text=True,
            capture_output=True
        )
        if process.returncode == 0:
            result_text = process.stdout.strip()
            logging.info(f"OntoGPT processing successful for input: {input_text}")
            return result_text
        else:
            logging.error(f"OntoGPT failed for input: {input_text}. Error: {process.stderr.strip()}")
            return None
    except Exception as e:
        logging.exception(f"Error during OntoGPT processing: {e}")
        return None

def process_data(data):
    try:
        input_text = data.get("message")
        if not input_text:
            logging.warning("Received empty message.")
            return None

        output = process_input_text(input_text)

        if output:
            try:
                output_json = json.loads(output)  
            except json.JSONDecodeError:
                output_json = [output]  
            payload = {
                "input_text": input_text,
                "output": output_json
            }
            logging.info("Sending processed message back to server.")
            requests.post(processed_message_url, json=payload)
        else:
            logging.warning("OntoGPT output empty. Sending error.")
            requests.post(error_message_url, json={"input_text": input_text, "error": "OntoGPT output was empty or failed."})
    except Exception as e:
        logging.exception(f"Error in process_data: {e}")
        try:
            requests.post(error_message_url, json={"input_text": input_text, "error": "Processing exception occurred."})
        except:
            logging.error("Failed to send error message to server.")

def on_open(ws):
    logging.info("WebSocket connection opened.")

def on_message(ws, message):
    logging.info(f"Message received from server: {message}")
    try:
        data = json.loads(message)
        if data.get("message") is not None:
            process_data(data)
        else:
            logging.warning("Message field is None.")
    except Exception as e:
        logging.exception(f"Failed to process received message: {e}")

def on_close(ws, close_status_code, close_msg):
    logging.warning(f"WebSocket closed: {close_status_code} - {close_msg}")

def on_error(ws, error):
    logging.error(f"WebSocket error: {error}")

def run_ws():
    while True:
        ws = websocket.WebSocketApp(
            websocket_url,
            on_open=on_open,
            on_message=on_message,
            on_close=on_close,
            on_error=on_error
        )
        try:
            logging.info("Attempting to connect to WebSocket server...")
            ws.run_forever(ping_interval=30, ping_timeout=10) 
        except Exception as e:
            logging.error(f"WebSocket run_forever exception: {e}")
        logging.info("WebSocket disconnected. Retrying in 5 seconds...")
        time.sleep(5)

if __name__ == "__main__":
    try:
        ws_thread = threading.Thread(target=run_ws, daemon=True)
        ws_thread.start()

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Shutdown requested. Exiting...")
