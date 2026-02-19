FROM python:3.13-slim

# Install dependencies
RUN mkdir /app
WORKDIR /app

RUN pip install --upgrade pip

COPY . .
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "main.py"]
