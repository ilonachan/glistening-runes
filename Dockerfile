FROM python:3.9

VOLUME /bot/config

WORKDIR /bot

# install required libraries
COPY ./requirements.txt /bot/requirements.txt
RUN pip install -r /bot/requirements.txt

# copy the code and default configuration
COPY ./runicbabble /bot/runicbabble
COPY ./logging.yaml /bot/logging.yaml

CMD [ "python", "-m", "runicbabble" ]