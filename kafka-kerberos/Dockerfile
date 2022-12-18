FROM debian:buster

EXPOSE 749 88/udp

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get -qq update
RUN apt-get -qq install locales krb5-kdc krb5-admin-server
RUN apt-get -qq install vim 
RUN apt-get -qq clean

ENV REALM ${REALM:-ALTINITY.TEST}
# Set the docker network name assigned to the containers in the principals 
# because if no dns service is used, the principals should be added with fqdn for kafka/zookeeper 
ENV DOMAIN_REALM ${DOMAIN_REALM:-altinity_default}
ENV KADMIN_PRINCIPAL ${KADMIN_PRINCIPAL:-kadmin}
ENV KADMIN_PASSWORD ${KADMIN_PASSWORD:-admin}

COPY init-script-kdc.sh /tmp/
CMD /tmp/init-script-kdc.sh

