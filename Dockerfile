FROM continuumio/anaconda3
WORKDIR /app
COPY bot.py bot.py
COPY controller.py controller.py
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
CMD ["flask", "--app bot.py", "run"]