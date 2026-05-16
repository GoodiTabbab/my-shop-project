# syntax=docker/dockerfile:1

FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 3000
CMD ["python3", "manage.py", "runserver", "0.0.0.0:3000"]
