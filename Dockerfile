FROM alpine:latest

RUN set -ex \
# install bash and mysql-client
    && apk add --no-cache bash mysql-client mariadb-connector-c

COPY monitoring /root/monitoring
RUN chmod +x /root/monitoring

CMD [ "/root/monitoring" ]
