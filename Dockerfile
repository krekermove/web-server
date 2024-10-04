FROM python:alpine

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN pip install --upgrade pip

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

WORKDIR /test-web-server

COPY . .

RUN chmod -R 777 ./

EXPOSE 8000
CMD ["python","manage.py","runserver","0.0.0.0:8000"]