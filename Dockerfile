
FROM docker:23.0.1-dind

RUN apk add --no-cache python3 py3-pip

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python3", "app.py"]
