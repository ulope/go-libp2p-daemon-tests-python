FROM golang:1.14 AS gobuild

RUN git clone -b v0.2.3 https://github.com/libp2p/go-libp2p-daemon /go-libp2p-daemon
WORKDIR /go-libp2p-daemon
RUN go get ./... && go install ./...


FROM python:3.7

COPY --from=gobuild /go/bin/p2pd /p2pd

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY main.py /main.py
COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
