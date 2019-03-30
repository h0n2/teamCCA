FROM hadoop-spark
MAINTAINER Venki Korukanti (venki.korukanti@gmail.com)

COPY scripts /usr/bin/.
RUN chmod 777 /usr/bin/bootstrap.sh
ENTRYPOINT ["/usr/bin/bootstrap.sh"]
