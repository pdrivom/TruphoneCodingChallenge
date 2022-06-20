import asyncio
from lib.kafka_topic_to_timescale import KafkaTopicToTimescaleDb



async def async_populate():
    await bridge.database.connect()
    await bridge.populate()
    await bridge.database.disconnect()

bridge = KafkaTopicToTimescaleDb('usage')
bridge.create_metadata()
bridge.connect()
asyncio.run(async_populate())


bridge.start_bridging()


