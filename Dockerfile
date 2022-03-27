from python:3.10.4-bullseye

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
