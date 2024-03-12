FROM python:3.10-slim

# Install dependencies
RUN mkdir /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install requests

COPY main.py .



#RUN ["python", "-m", "main.py"]

ENTRYPOINT ["python", "main.py"]
