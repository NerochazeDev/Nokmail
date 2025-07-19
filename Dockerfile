FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install python-telegram-bot==22.2 python-dotenv==1.1.1 requests==2.32.4

# Create necessary directories
RUN mkdir -p data templates

EXPOSE 5000

CMD ["python", "simple_main.py"]