import logging
import sys

from pyflink.common import Row
from pyflink.common.typeinfo import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer
from pyflink.datastream.formats.json import JsonRowDeserializationSchema


def highest_price_per_stock():
    """
    Flink job to calculate the highest trade price per stock from a Kafka topic.
    """
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)

    # Define the Kafka consumer properties
    kafka_props = {
        'bootstrap.servers': 'kafka:29092',
        'group.id': 'tickerflow-flink-consumer'
    }

    # Define the type information for the JSON data
    type_info = Types.ROW_NAMED(
        ['symbol', 'timestamp', 'exchange', 'price', 'size', 'id', 'conditions', 'tape'],
        [Types.STRING(), Types.STRING(), Types.STRING(), Types.FLOAT(), 
         Types.FLOAT(), Types.LONG(), Types.LIST(Types.STRING()), Types.STRING()]
    )
    
    # JSON Deserialization Schema
    json_deserialization_schema = JsonRowDeserializationSchema.builder() \
        .type_info(type_info).build()

    # Create a Kafka consumer
    kafka_consumer = FlinkKafkaConsumer(
        topics='ticker_events',
        deserialization_schema=json_deserialization_schema,
        properties=kafka_props
    )

    # Add the Kafka source to the environment
    data_stream = env.add_source(kafka_consumer)

    # Process the stream to find the highest price per stock
    # Key by symbol and keep track of the highest price
    def reduce_highest_price(acc, new):
        return Row(
            symbol=new.symbol,
            timestamp=new.timestamp,
            exchange=new.exchange,
            price=max(acc.price, new.price),
            size=new.size,
            id=new.id,
            conditions=new.conditions,
            tape=new.tape
        )
    
    highest_price_stream = data_stream \
        .key_by(lambda row: row.symbol) \
        .reduce(reduce_highest_price)

    formatted_output_stream = highest_price_stream.map(
        lambda trade: f"Symbol: {trade.symbol}, Highest Price: {trade.price}",
        output_type=Types.STRING()
    )
    
    formatted_output_stream.print()
    
    # # Print the results to the console
    # highest_price_stream.print()

    # Execute the Flink job
    env.execute("Highest Price Per Stock")


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")
    highest_price_per_stock()
