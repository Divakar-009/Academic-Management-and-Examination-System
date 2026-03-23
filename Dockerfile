FROM python:3.12

WORKDIR /app

RUN apt-get update && apt-get install -y netcat-openbsd


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "python manage.py migrate && daphne -b 0.0.0.0 -p 8000 core.asgi:application"]