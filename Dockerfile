FROM python:3.11-slim-bookworm

WORKDIR /app

# Install ontogpt
RUN apt update && apt install -y gcc
RUN pip install --upgrade pip && pip install ontogpt==1.0.10

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

EXPOSE 8000

CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "8000"]

