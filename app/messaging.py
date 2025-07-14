import asyncio

class MessageBroker:
    def __init__(self):
        self.topics = {}

    def create_topic(self, topic_name):
        if topic_name not in self.topics:
            self.topics[topic_name] = asyncio.Queue()

    async def publish(self, topic_name, message):
        if topic_name in self.topics:
            await self.topics[topic_name].put(message)

    def subscribe(self, topic_name, handler):
        async def listen():
            while True:
                message = await self.topics[topic_name].get()
                await handler(message)

        asyncio.create_task(listen())

        

broker = MessageBroker()
broker.create_topic("doc_uploaded")
