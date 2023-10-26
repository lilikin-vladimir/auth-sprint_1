FROM python:3.10

WORKDIR /usr/src/app

COPY wait-for-it.sh wait-for-etl.sh .
RUN chmod +x wait-for-it.sh && chmod +x wait-for-etl.sh

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./src .
#COPY ./data ../data

CMD ["./wait-for-etl.sh", "--", "python3", "main.py"]
