import asyncio

class MessageBroker:
    def __init__(self):
        self.topics = {}

    def create_topic(self, topic_name):
        if topic_name not in self.topics:
            print(f" [Broker] Created topic: {topic_name}")
            self.topics[topic_name] = asyncio.Queue()

    async def publish(self, topic_name, message):
        if topic_name in self.topics:
            print(f" [Broker] Publishing message to '{topic_name}': {message}")
            await self.topics[topic_name].put(message)
        else:
            print(f" [Broker] Tried to publish to non-existent topic: {topic_name}")

    def subscribe(self, topic_name, handler):
        async def listen():
            print(f" [Broker] Subscribed and listening to '{topic_name}'")
            while True:
                message = await self.topics[topic_name].get()
                print(f" [Broker] Received message on '{topic_name}': {message}")
                await handler(message)

        asyncio.create_task(listen())


broker = MessageBroker()
broker.create_topic("doc_uploaded")

 