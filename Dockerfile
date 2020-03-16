FROM python
WORKDIR /app
RUN apt update && \
    apt install -y libusb-1.0-0-dev libudev-dev && \
    rm -rf /var/apt/lists/*
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py app.py
CMD ["python", "app.py"]