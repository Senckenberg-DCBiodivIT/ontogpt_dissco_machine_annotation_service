import subprocess
import uvicorn
import logging
import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pydantic_settings import BaseSettings

class Inputtext(BaseModel):
    input_text: str

class ProcessedMessageRequest(BaseModel):
    input_text: str
    output: list

class ErrorMessageRequest(BaseModel):
    input_text: str
    error: str

class Settings(BaseSettings):
    log_level: str = "DEBUG"
    template_path: str = "habitat_template_v2.yaml"
    llm_model: str = "ollama/mistral"

settings = Settings()
logging.basicConfig(level=logging.getLevelNamesMapping()[settings.log_level])

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    logging.info(f"Starting application with template={settings.template_path}, model={settings.llm_model}")

@app.post("/extract_ontogpt")
async def extract_ontogpt(request: Inputtext):
    try:
        input_text = request.input_text
        logging.info(f"Processing input text: {input_text}")
        process = subprocess.run(
            ['ontogpt', '-v', 'extract', '-t', settings.template_path, '-m', settings.llm_model, '-O', 'json'],
            input=input_text,
            text=True,
            capture_output=True
        )
        logging.debug("OntoGPT message: " + process.stderr)
        if process.returncode == 0:
            result_text = process.stdout.strip()
            logging.info(f"OntoGPT processing successful for input: {input_text}")
            return JSONResponse(content=json.loads(result_text))
        else:
            logging.error(f"OntoGPT failed for input: {input_text}. Error: {process.stderr.strip()}")
            raise HTTPException(status_code=500, detail="OntoGPT processing error")

    except Exception as e:
        logging.error(f"Error in the ontogpt tool: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the input text: {input_text}")



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
