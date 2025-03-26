from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    log_level: str = "DEBUG"
    template_path: str = "habitat_template_v2.yaml"
    llm_model: str = "ollama/mistral"
    port: int = 80
    host: str = "0.0.0.0"
    ontogpt_path_to_binary = "ontogpt"