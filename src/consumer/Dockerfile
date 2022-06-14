FROM python:3-alpine

WORKDIR /usr/src/consumer

COPY requirements.txt ./
RUN apk add --no-cache python3 postgresql-libs
RUN apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev postgresql-dev
RUN pip install --upgrade --no-cache-dir -r requirements.txt
RUN apk --purge del .build-deps

COPY . .

CMD ["python","-u","consumer.py"]
