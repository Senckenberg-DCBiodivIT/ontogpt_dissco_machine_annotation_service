import subprocess
import uvicorn
import logging

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)

class Inputtext(BaseModel):
    input_text: str

class ProcessedMessageRequest(BaseModel):
    input_text: str
    output: list

class ErrorMessageRequest(BaseModel):
    input_text: str
    error: str


template_path = "habitat_template_v2.yaml"


app = FastAPI()

@app.post("/extract_ontogpt")
async def extract_ontogpt(request: Inputtext):
    try:
        input_text = request.input_text
        process = subprocess.run(
            ['ontogpt', '-v', 'extract', '-t', template_path, '-m', 'ollama/mistral'],
            input=input_text,
            text=True,
            capture_output=True
        )
        if process.returncode == 0:
            result_text = process.stdout.strip()
            logging.info(f"OntoGPT processing successful for input: {input_text}")
            return JSONResponse(content=result_text)
        else:
            logging.error(f"OntoGPT failed for input: {input_text}. Error: {process.stderr.strip()}")
            raise HTTPException(status_code=409, detail="OntoGPT processing error")

    except Exception as e:
        logging.error(f"Error in the ontogpt tool: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the input text: {input_text}")



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
