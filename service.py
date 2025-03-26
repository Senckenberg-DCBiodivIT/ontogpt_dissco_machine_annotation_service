import subprocess
import uvicorn
import logging
import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .config import Settings


class Inputtext(BaseModel):
    input_text: str

class NamedEntity(BaseModel):
    id: str
    label: str

class ProcessedMessageRequest(BaseModel):
    named_entities: list[NamedEntity]

class ErrorMessageRequest(BaseModel):
    input_text: str
    error: str


settings = Settings()
logging.basicConfig(level=logging.getLevelNamesMapping()[settings.log_level])

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    logging.info(f"Starting application with template={settings.template_path}, model={settings.llm_model}")

def parse_ontogpt_result(result: str) -> list[NamedEntity]:
    result_json = json.loads(result)
    named_entities = []
    if "named_entities" in result_json:
        for entity in result_json["named_entities"]:
            parsed_entity = NamedEntity(id=entity['id'], label=entity['label'])
            if parsed_entity.id.startswith("AUTO"):
                logging.info(f"Ignore entity: {parsed_entity.id} (AUTO in label)")
                continue
            named_entities.append(parsed_entity)

    return named_entities

@app.post("/extract_ontogpt")
async def extract_ontogpt(request: Inputtext) -> ProcessedMessageRequest:
    try:
        input_text = request.input_text
        logging.info(f"Processing input text: {input_text}")
        process = subprocess.run(
            [settings.ontogpt_path_to_binary, '-v', 'extract', '-t', settings.template_path, '-m', settings.llm_model, '-O', 'json'],
            input=input_text,
            text=True,
            capture_output=True
        )
        logging.debug("OntoGPT message: " + process.stderr)

        if process.returncode == 0:
            result_text = process.stdout.strip()
            logging.info(f"OntoGPT processing successful for input: {input_text}")
            named_entities = parse_ontogpt_result(result_text)
            return ProcessedMessageRequest(named_entities=named_entities)
        else:
            logging.error(f"OntoGPT failed for input: {input_text}. Error: {process.stderr.strip()}")
            raise HTTPException(status_code=500, detail="OntoGPT processing error")

    except Exception as e:
        logging.error(f"Error in the ontogpt tool: {e}", e)
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the input text: {input_text}")



if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)
