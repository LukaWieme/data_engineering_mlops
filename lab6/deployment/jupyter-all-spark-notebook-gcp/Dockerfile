FROM quay.io/jupyter/all-spark-notebook:spark-4.2.0
USER root
# add bigquery, kafka, and gsc dependencies
RUN echo 'spark.jars.packages com.google.guava:failureaccess:1.0.3,com.google.guava:guava:33.7.2-jre,com.google.cloud.spark:spark-bigquery-with-dependencies_2.13:0.46.0,com.google.cloud.bigdataoss:gcs-connector:hadoop3-2.2.33,org.apache.spark:spark-streaming-kafka-0-10_2.13:4.2.0' >> "${SPARK_HOME}/conf/spark-defaults.conf"
