FROM python:3.10

# Configure default directory structure
WORKDIR /app
RUN mkdir /library

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy program and start the flask server
# TODO: use a production server here instead, like uwsgi
COPY DingDongWeb.py .
CMD [ 'python3', '-m', 'flask', 'run', '--host=0.0.0.0']
