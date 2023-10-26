FROM python:3.10

WORKDIR /app

COPY wait-for-it.sh wait-for-tests.sh restore_elasticsearch.sh entrypoint.sh ./
RUN chmod +x wait-for-it.sh && \
    chmod +x wait-for-tests.sh && \
    chmod +x restore_elasticsearch.sh && \
    chmod +x entrypoint.sh

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["./wait-for-tests.sh", "--", "/app/entrypoint.sh"]
