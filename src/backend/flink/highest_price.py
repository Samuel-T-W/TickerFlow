import logging
import sys
import os
from datetime import datetime, timezone

from pyflink.datastream.state import ValueStateDescriptor
from redis_sink import RedisWriter

from pyflink.common import Row
from pyflink.common.typeinfo import Types
from pyflink.datastream import KeyedProcessFunction, StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer
from pyflink.datastream.formats.json import JsonRowDeserializationSchema
from dataclasses import dataclass, asdict

@dataclass
class SingleValueStat:
    symbol: str
    stat_name: str  # i.e "highest_price", "lowest_price"
    value: float
    trade_date: str
    last_updated: str

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "stat_name": self.stat_name,
            "value": self.value,
            "trade_date": self.trade_date,
            "last_updated": self.last_updated
        }


def single_value_stocks():
    """
    Flink job to calculate the highest trade price per stock from a Kafka topic.
    """
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)

    # Dependency files must be added so TaskManagers can find them
    current_dir = os.path.dirname(os.path.abspath(__file__))
    redis_sink_path = os.path.join(current_dir, 'redis_sink.py')
    env.add_python_file(redis_sink_path)

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
    
    single_value_stats = data_stream \
        .key_by(lambda row: row.symbol) \
        .process(SingleValueStats())

    # Execute the Flink job
    env.execute("Highest Price Per Stock")
    

class SingleValueStats(KeyedProcessFunction):
    def __init__(self):
        self.redis_writer = None

    def open(self, runtime_context):
        self.redis_writer = RedisWriter()
        self.redis_writer.open()
        
        # single value stats
        max_desc = ValueStateDescriptor("max_price", Types.FLOAT())
        self.max_price = runtime_context.get_state(max_desc)
        
        min_price = ValueStateDescriptor("min_price", Types.FLOAT())
        self.min_price = runtime_context.get_state(min_price)
        
                            
    
    def process_element(self, value, ctx):
        # TODO: figure out how the day affects the stat value calc's since these are technically windows but of size 1 day?
        
        # Extract date from timestamp for daily partitioning
        try:
            trade_date = datetime.fromisoformat(value.timestamp.replace('Z', '+00:00')).date().isoformat()
        except Exception as e:
            logging.error(f"Error extracting timestamp from data:{value.timestamp} and symbol: {value.symbol}. Error: {e}")
            return
        
        # check new trade price with max price so far and only update and wirte if its greater than
        max_price = self.max_price.value()
        if max_price is None:
            max_price = float("-inf")
        if value.price > max_price:
            self.max_price.update(value.price)
            data = prepare_redis_value_data("highest_price", value.price, trade_date, value)
            self.redis_writer.write(key=f"highest_price:{trade_date}:{value.symbol}", data=data.to_dict())
        
        # check new trade price with min price so far and only update and wirte if its lesser than
        min_price = self.min_price.value()
        if min_price is None:
            min_price = float('inf')
        if value.price < min_price:
            self.min_price.update(value.price)
            data = prepare_redis_value_data("lowest_price", value.price, trade_date, value)
            self.redis_writer.write(key=f"lowest_price:{trade_date}:{value.symbol}", data=data.to_dict())
        
        #TODO: figure out how to update latest trade only to some significant factors a 0.00001 cahnge should not cause an update
        data = prepare_redis_value_data("latest_trade", value.price, trade_date, value)
        logging.info(f"data:{data}: data_dict:{asdict(data)} data_dict:{data.to_dict()}")
        self.redis_writer.write(key=f"latest_trade:{trade_date}:{value.symbol}", data=data.to_dict())
        
    
    def close(self):
        self.redis_writer.close()
        
        
    
def prepare_redis_value_data(stat_name: str, value: float, trade_date: str, event)-> SingleValueStat:    
    return SingleValueStat(
        symbol = event.symbol,
        stat_name = stat_name,
        value = value,
        trade_date = trade_date,
        last_updated = datetime.now(timezone.utc).isoformat()
    )


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")
    single_value_stocks()
