FROM ubuntu:20.04

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3

RUN pip3 install --upgrade pip

#RUN adduser worker
RUN useradd -s /bin/bash -d /home/worker -m -G sudo worker
USER worker
WORKDIR /home/worker

COPY --chown=worker:worker requirements.txt requirements.txt
RUN pip3 install --user -r requirements.txt

ENV PATH="/home/worker/.local/bin:${PATH}"

COPY --chown=worker:worker . .

LABEL maintainer="warpnow@gmail.com" \
      version="1.0.0"

WORKDIR /home/worker/src
CMD python3 pyom.py
