FROM jfloff/alpine-python:3.6-onbuild 
COPY requirements.txt /tmp 
WORKDIR /tmp 
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
WORKDIR /.
ADD heater_rules.py /
CMD [ "python", "./heater_rules.py" ]
