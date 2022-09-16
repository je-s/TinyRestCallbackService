FROM    debian:11
LABEL   maintainer="JES <je@aesyc.systems>" \
        version="1.0"
ENV     DEBIAN_FRONTEND noninteractive
RUN     apt-get clean && apt-get update
RUN     apt-get install -y \
        build-essential \
        python3 python3-pip
RUN     mkdir /TinyHttpCallbackService
COPY    ./ /TinyHttpCallbackService/
WORKDIR /TinyHttpCallbackService/
RUN     pip3 install -r requirements.txt
ENTRYPOINT [ "/usr/bin/python3", "-u", "tinyhttpcallbackservice.py", "data/config.toml" ]