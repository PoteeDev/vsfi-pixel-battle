FROM python:3.9-alpine
WORKDIR /api
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
EXPOSE 5000
CMD gunicorn -b 0.0.0.0:5000 --workers 16 --threads 100 main:app