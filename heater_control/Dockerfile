FROM tiangolo/meinheld-gunicorn-flask:python3.7
COPY requirements.txt /tmp 
WORKDIR /tmp 
ARG TZ=Australia/Melbourne
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
WORKDIR /.
COPY . /app

