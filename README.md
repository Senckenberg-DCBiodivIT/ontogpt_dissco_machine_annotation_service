# ontogpt_dissco_machine_annotation_service

## On the proxy backend:
```
python -m venv venv
source venv/bin/activate
pip install -r requirements_service.txt
python service.py
```

## On the (GPU-Powered) backend:
```
python -m venv venv
source venv/bin/activate
pip install -r requirements_inference.txt
python process_ontogpt.py
```