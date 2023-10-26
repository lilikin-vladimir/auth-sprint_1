FROM python:3.10

WORKDIR /app

COPY wait-for-it.sh wait-for-async_api.sh .
RUN chmod +x wait-for-it.sh && chmod +x wait-for-async_api.sh

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./src .

CMD ["./wait-for-async_api.sh", "--", "gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "main:app"]
