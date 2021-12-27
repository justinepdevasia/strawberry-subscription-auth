from __future__ import annotations


import strawberry
from broadcaster import Broadcast
from strawberry.types import Info


import json
import datetime
from typing import Optional

from .custom_auth import IsAuthenticated, AuthGraphQLRouter



# broadcast = Broadcast("redis://localhost:6379")  # redis pub sub
# broadcast = Broadcast('postgres://postgres:postgres@localhost:5432/broadcaster')
broadcast = Broadcast('memory://') # for in memory pub sub


@strawberry.type
class Message:
    timestamp: str
    owner: str
    content: str


# send message to queue once it is received
async def process_message(message: Message, channel: str):
    message_json = json.dumps(message.__dict__, indent=4)
    await broadcast.publish(channel=channel, message=message_json)
    print(f"message added to broadcast channel")


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_message(self, info: Info, name: str, content: str, channel: str) -> bool:
        message = Message(timestamp=str(datetime.datetime.now()), owner=name, content=content)
        await process_message(message, channel)
        return True


@strawberry.type
class Subscription:
    @strawberry.subscription(permission_classes=[IsAuthenticated])
    async def get_push_message(self,channel: str) -> Message:
        print(f"message ready to be received")
        async with broadcast.subscribe(channel=channel) as subscriber:
            async for event in subscriber:
                yield Message(**json.loads(event.message))


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "World"

schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)
graphql_app = AuthGraphQLRouter(schema, graphiql=True)



