FROM alpine:latest

RUN set -ex \
# install bash and mysql-client
    && apk add --no-cache bash mysql-client

COPY monitoring /usr/sbin

CMD [ "monitoring" ]