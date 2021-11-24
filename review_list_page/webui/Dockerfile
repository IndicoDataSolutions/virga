## DEVELOPMENT
FROM node:14-alpine as development

# configure env vars for runtime
ENV APP_NAME=review_list_page-webui \
    WEBUI_PORT=8080

# install system dependencies
RUN apk update && \
    apk add --no-cache curl vim postgresql-client bash && \
    deluser --remove-home node

# copy and install app dependencies
COPY ./package.json ./yarn.lock /review_list_page-webui/
WORKDIR /review_list_page-webui
RUN yarn install

# copy everything over
COPY . /review_list_page-webui

# start the development server
CMD [ "yarn", "start" ]


## PRODUCTION
# build the static UI files for serving via nginx
FROM development as production
RUN yarn build

FROM gcr.io/new-indico/nginx:1.15.10
COPY --from=production /review_list_page-webui/build /review_list_page-webui/build