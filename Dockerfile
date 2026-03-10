FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY detectors/ detectors/
COPY analyzers/ analyzers/
COPY solvers/ solvers/
COPY templates/ templates/

RUN mkdir -p uploads

EXPOSE 5000

CMD ["python", "app.py"]
