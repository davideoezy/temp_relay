FROM ubuntu:latest
COPY requirements.txt /tmp 
WORKDIR /tmp 
RUN apk add --update tzdata
ENV TZ=Australia/Melbourne
RUN pip install --upgrade pip
RUN apt update && apt install -y libmariadb3 libmariadb-dev && rm -rf /var/lib/apt/lists/*
RUN pip3 install -r requirements.txt
WORKDIR /.
COPY . /

CMD [ "python3", "./heater_control_to_mqtt.py" ]
