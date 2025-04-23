
FROM python:3.10

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN playwright install --with-deps

CMD ["python", "watcher_twitter.py"]
