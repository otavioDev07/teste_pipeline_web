FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    g++ \
    libopencv-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN g++ -std=c++17 -O3 RDP+HoughProb/detector.cpp -o RDP+HoughProb/detector $(pkg-config --cflags --libs opencv4)
RUN chmod +x pipeline.sh

CMD gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120