FROM golang:alpine

LABEL maintainer="Alvaro Gomez"

WORKDIR /go/src/app

ADD . .

RUN go mod init && go build -o helloworld

EXPOSE 6111

CMD ["./helloworld"]