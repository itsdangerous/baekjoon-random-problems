FROM python:3.11.6-slim

WORKDIR ./app

#libgl1-mesa-glx 패키지 설치
RUN apt-get update && apt-get -y install libgl1-mesa-glx
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005"]
