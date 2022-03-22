FROM python:3.8.10
WORKDIR /app/python
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY / .
CMD ["python", "driver_04.py"]
