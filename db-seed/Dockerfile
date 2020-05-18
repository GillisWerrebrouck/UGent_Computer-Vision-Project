FROM node:10-alpine

RUN apk add --no-cache yarn

WORKDIR /app

# add dependencies to container so they are not fetched every time
ADD package.json yarn.lock /app/
RUN yarn

CMD yarn start
