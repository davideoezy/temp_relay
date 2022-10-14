FROM ubuntu:latest
COPY requirements.txt /tmp 
WORKDIR /tmp 
#RUN apt add --update tzdata
ENV TZ=Australia/Melbourne
RUN apt update && apt install -y libmariadb3 libmariadb-dev python-pip && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt
WORKDIR /.
COPY . /

CMD [ "python3", "./heater_control_to_mqtt.py" ]
