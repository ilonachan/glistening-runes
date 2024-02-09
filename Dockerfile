FROM python:3.10

VOLUME /bot/config

WORKDIR /bot

RUN useradd -m -r user && \
    chown user /bot

# install required libraries
COPY requirements.txt ./
RUN pip install -r requirements.txt

# copy the code and default configuration
COPY ./runicbabble ./runicbabble
COPY ./logging.yaml ./

ARG GIT_HASH
ENV GIT_HASH=${GIT_HASH:-dev}

USER user

CMD [ "python", "-m", "runicbabble" ]
