FROM    debian:11
LABEL   maintainer="JES <je@aesyc.systems>" \
        version="1.0"
ENV     DEBIAN_FRONTEND noninteractive
RUN     apt-get clean && apt-get update
RUN     apt-get install -y \
        build-essential \
        python3 python3-pip
RUN     mkdir /TinyRestCallbackService
COPY    ./ /TinyRestCallbackService/
WORKDIR /TinyRestCallbackService/
RUN     pip3 install -r requirements.txt
ENTRYPOINT [ "/usr/bin/python3", "-u", "tinyrestcallbackservice.py", "data/config.toml" ]