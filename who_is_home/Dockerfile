FROM jfloff/alpine-python:3.6-onbuild 
COPY requirements.txt /tmp 
WORKDIR /tmp 
RUN pip install --upgrade pip
RUN pip install mysql-connector
WORKDIR /.
ADD somebody_home.py /
CMD [ "python", "./somebody_home.py" ]
