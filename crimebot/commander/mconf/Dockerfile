FROM alpine:latest
RUN apk add --no-cache docker curl openssh git
RUN mkdir -p /app
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
RUN git clone https://github.com/rapid7/metasploit-framework.git /opt/metasploit-framework
RUN cd /opt/metasploit-framework && git checkout master && ./msfupdate
