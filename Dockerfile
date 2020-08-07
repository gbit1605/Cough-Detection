# start with a base image
FROM ubuntu:18.04
MAINTAINER Team Mockingjays <mockingjaysteam@gmail.com>
# install dependencies
RUN apt-get update -y && apt-get install -y python3-pip python3-dev libsm6 libxext6 libxrender-dev
RUN apt-get install -y libglib2.0-dev
RUN apt-get install -y libsndfile1-dev
RUN apt-get install -y ffmpeg
RUN apt-get install -y --no-install-recommends openssh-server
#We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
COPY . /app
EXPOSE 8000
ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]
