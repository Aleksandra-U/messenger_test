FROM python:3.12

RUN mkdir /messanger

WORKDIR /messanger

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x /messanger/docker/*.sh

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind=0.0.0.0:8000"]