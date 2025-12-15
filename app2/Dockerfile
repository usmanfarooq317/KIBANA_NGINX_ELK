FROM python:3.9-slim

WORKDIR /app

# Create log directory
RUN mkdir -p /fluent-bit/logs/app1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

CMD ["python", "app.py"]