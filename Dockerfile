# Yeh base image Playwright ne officially banayi hai jisme saari Linux dependencies pehle se hoti hain
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# Working directory set kar rahe hain
WORKDIR /app

# Requirements copy karke install karna
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Saara code copy karna
COPY . .

# Server start karne ka command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
