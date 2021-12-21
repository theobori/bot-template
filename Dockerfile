FROM python:3.8-slim

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y

RUN pip3 install -r requirements.txt

CMD ["python3", "main.py"]

# docker build -t teeskins .
# docker run -it -v $PWD/public:/app/public teeskins