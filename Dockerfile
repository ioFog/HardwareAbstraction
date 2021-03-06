FROM frolvlad/alpine-python3

RUN apk add --update util-linux pciutils lshw # basic linux utils for HWC
RUN apk add --update build-base python3-dev # lastest python dev utils
RUN pip install --upgrade pip
RUN pip install pyserial
RUN pip install autobahn

COPY . /src/
RUN cd /src;

CMD ["python3", "/src/hal_main.py"]