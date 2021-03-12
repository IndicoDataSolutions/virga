FROM nginx:stable-alpine

RUN apk upgrade --update-cache --available && \
    apk add openssl && \
    rm -rf /var/cache/apk/*

RUN openssl req -x509 -newkey rsa:4096 -sha256 -nodes -subj '/CN=app.indico.local' -keyout /etc/ssl/private/app-indico-local.key -out /etc/ssl/private/app-indico-local.crt 

COPY app-indico-local.conf /etc/nginx/conf.d/app-indico-local.conf