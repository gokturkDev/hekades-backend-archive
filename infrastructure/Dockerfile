# Use python 3.12
FROM python:3.12

#COPY PACKAGES
WORKDIR /app

COPY ../business ./business
COPY ../data ./data
COPY ../interface ./interface
COPY ../ai ./ai
COPY ../infrastructure ./infrastructure
COPY ../core ./core
COPY ../main ./main
RUN mkdir ./logs

ARG AWS_SECRET_NAME
ARG AWS_SECRET_REGION

ENV PYTHONUNBUFFERED=1
ENV AWS_LOGS_ACTIVE=1
ENV AWS_SECRET_NAME=$AWS_SECRET_NAME
ENV AWS_SECRET_REGION=$AWS_SECRET_REGION

RUN pip install --no-cache-dir -r ./infrastructure/requirements.txt
EXPOSE 80

CMD ["uvicorn", "main.app:app", "--loop", "asyncio", "--host", "0.0.0.0", "--port", "80"]