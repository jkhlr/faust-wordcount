FROM python:3.8-buster

WORKDIR /var/wordcount
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY vep_data vep_data
COPY word_count word_count
COPY pytest.ini pytest.ini

ENTRYPOINT ["word_count/main.py"]