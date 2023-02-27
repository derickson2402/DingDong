FROM python:3.10

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt && rm -f requirements.txt

# Copy program and start the flask server
# TODO: use a production server here instead, like uwsgi
WORKDIR /app
COPY DingDongWeb.py DingDongWeb.py
COPY DingDongDB.py DingDongDB.py
ENV FLASK_APP DingDongWeb.py
CMD [ "python3", "-m", "flask", "run", "--host=0.0.0.0"]
