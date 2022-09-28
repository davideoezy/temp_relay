FROM tiangolo/meinheld-gunicorn-flask:latest
COPY requirements.txt /tmp 
WORKDIR /tmp 
ARG TZ=Australia/Melbourne
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN pip install --upgrade pip
RUN apt update && apt install -y libmariadb3 libmariadb-dev && rm -rf /var/lib/apt/lists/*
RUN pip3 install -r requirements.txt
WORKDIR /.
COPY . /app

