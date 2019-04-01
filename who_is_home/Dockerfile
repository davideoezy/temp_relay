FROM jfloff/alpine-python:3.6-onbuild 
COPY requirements.txt /tmp 
WORKDIR /tmp 
RUN pip install -r requirements.txt 
WORKDIR /.
ADD somebody_home.py /
CMD [ "python", "./somebody_home.py" ]