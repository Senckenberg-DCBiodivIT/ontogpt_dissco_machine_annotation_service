import os
import uvicorn
import asyncio
import logging

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict

logging.basicConfig(level=logging.INFO)

class Inputtext(BaseModel):
    input_text: str

class ProcessedMessageRequest(BaseModel):
    input_text: str
    output: list

class ErrorMessageRequest(BaseModel):
    input_text: str
    error: str

message_queue: List[str] = []
processed_messages: Dict[str, Dict] = {}
error_messages: Dict[str, Dict] = {}
active_connections: List[WebSocket] = []

app = FastAPI()

@app.post("/extract_ontogpt")
async def extract_ontogpt(request: Inputtext):
    try:
        message_queue.append(request.input_text)
        timeout = 200
        start_time = asyncio.get_event_loop().time()

        while request.input_text not in processed_messages and (asyncio.get_event_loop().time() - start_time) <= timeout:
            if request.input_text in error_messages:
                error_data = error_messages[request.input_text]["error"]
                response = JSONResponse(content={"error": error_data}, status_code=500)
                del error_messages[request.input_text]
                return response
            await asyncio.sleep(1)

        if request.input_text not in processed_messages:
            return JSONResponse(content={"error": "Processing took too long."}, status_code=504)

        response_data = processed_messages[request.input_text]
        del processed_messages[request.input_text]
        return JSONResponse(content=response_data)

    except Exception as e:
        logging.error(f"Error in the ontogpt tool: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the input text: {str(e)}")

@app.websocket("/ws/new_message")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    logging.info("WebSocket client connected.")

    try:
        while websocket.application_state == WebSocketState.CONNECTED:
            if message_queue:
                message = message_queue.pop(0)
                await websocket.send_json({"message": message})
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logging.info("WebSocket client disconnected.")
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)

@app.post("/error_message")
async def error_message(request: ErrorMessageRequest):
    error_message = {
        "input_text": request.input_text,
        "error": request.error
    }
    error_messages[request.input_text] = error_message
    return {"message": "Error stored."}

@app.post("/processed_message")
async def processed_message(request: ProcessedMessageRequest):
    try:
        processed_data = {
            "input_text": request.input_text,
            "output": request.output
        }
        processed_messages[request.input_text] = processed_data
        return {"message": "Processed data stored successfully."}
    except Exception as e:
        logging.error(f"Error storing processed message: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the message: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
