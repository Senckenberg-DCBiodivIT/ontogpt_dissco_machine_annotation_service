# ontogpt_dissco_machine_annotation_service

## Installation

```bash
pip install -r requirements.txt
```

## Run

```bash
python service.py
```

or

```bash
fastapi run service.py
```

### Configuration

The app can be configured via pydantic-settings. See [here](https://fastapi.tiangolo.com/advanced/settings)

| Setting | Description | Default |
| ------- | ----------- | ------- |
| log_level | log level | INFO    |
| template_path | Path to otogpt template | habitat_template_v2.yaml |
| llm_model | LLM model to use | ollama/mistral |

TODO: Document/Configure how to use bioportal api key

## Develop

For develop, you can run it in dev mode which automatically reload changes

```bash
fastapi dev service.py
```

