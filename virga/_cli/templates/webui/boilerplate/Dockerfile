FROM node:14-buster-slim

RUN apt update && \
    apt install -y curl vim

COPY . /mini-strat
WORKDIR /mini-strat

RUN yarn install && \
    npx mkcert create-ca && \
    npx mkcert create-cert --key snowpack.key --cert snowpack.crt --domains app.indico.local

EXPOSE 443

ENTRYPOINT [ "yarn" ]
CMD [ "start" ]