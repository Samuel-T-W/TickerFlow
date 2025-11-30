# Use an official Flink image with Python 3.12
FROM flink:1.18.0-scala_2.12

# Flink's home directory
ENV FLINK_HOME=/opt/flink

# The Flink Kafka connector is not bundled with the official image, we need to add it.
# See: https://nightlies.apache.org/flink/flink-docs-release-1.18/docs/connectors/datastream/kafka/
# We are using the Kafka 3 connector to match our Kafka version.
RUN wget https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-kafka/3.1.0-1.18/flink-sql-connector-kafka-3.1.0-1.18.jar -O $FLINK_HOME/lib/flink-sql-connector-kafka.jar

# Switch to the root user to install dependencies
USER root

# Install Python and JDK for PyFlink jobs (JDK needed for pemja dependency)
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv openjdk-11-jdk-headless && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME for pemja compilation
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-arm64

ENV PYTHONPATH=/opt/flink/opt/python

# Install PyFlink and required Python dependencies
# Let pip resolve protobuf version automatically to avoid conflicts with apache-beam
RUN pip install --no-cache-dir "apache-flink==1.18.1" "redis>=5.0.0,<6.0.0"

# Let Flink know which Python executable to use
ENV PYFLINK_CLIENT_EXECUTABLE=/usr/bin/python3

# Set the working directory
WORKDIR /app

# Copy the Flink job module
COPY src/backend/flink /app/flink/
