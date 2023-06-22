FROM python:3.11.3-slim

WORKDIR /app

COPY . .

RUN pip install -r tools/requirements/base.txt

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

CMD ["uvicorn", "settings.asgi:application", "--host", "0.0.0.0", "--port", "8000"]