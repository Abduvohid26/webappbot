FROM python:3.11.4-slim-buster

WORKDIR /bot

# Ngrok ni o'rnatish
RUN apt-get update && apt-get install -y wget unzip
RUN wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
RUN unzip ngrok-stable-linux-amd64.zip -d /usr/local/bin/
RUN rm ngrok-stable-linux-amd64.zip

# Python kutubxonalarini o'rnatish
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Loyiha fayllarini nusxalash
COPY . .

# Ngrok tokenini sozlash (agar kerak bo'lsa)
# ENV NGROK_TOKEN="your_ngrok_token"

# Ngrok ni ishga tushirish va URL ni olish
CMD ["sh", "-c", "ngrok http 8080 & sleep 5 && python get_ngrok_url.py && uvicorn hook:app --host 0.0.0.0 --port 8080"]
# CMD ["sh", "-c", "uvicorn hook:app --host 0.0.0.0 --port 9090"]