FROM python:3-alpine

WORKDIR /usr/src/api

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

COPY . .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]