# set base image (host OS)
FROM python:3.8

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt .
#COPY current_price.py .

# install dependencies
RUN pip install -r requirements.txt
#RUN pip install sqlalchemy requests pandas pymysql

# copy the content of the local src directory to the working directory
COPY *.py ./

# command to run on container start
CMD ["python3", "-u", "/code/main.py"]