FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

EXPOSE 8000

CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "8000"]

