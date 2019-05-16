FROM tiangolo/meinheld-gunicorn-flask:python3.7
COPY requirements.txt /tmp 
WORKDIR /tmp 
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
WORKDIR /.
COPY . /app

