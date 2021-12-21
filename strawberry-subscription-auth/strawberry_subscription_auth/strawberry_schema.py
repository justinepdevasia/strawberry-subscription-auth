from __future__ import annotations


import strawberry
from broadcaster import Broadcast
from strawberry.fastapi import GraphQLRouter
from strawberry.fastapi.handlers import GraphQLWSHandler
from strawberry.subscriptions.protocols.graphql_ws.types import OperationMessage
from strawberry.types import Info
 




import json
import datetime
from typing import Optional

from .custom_auth import IsAuthenticated





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
        async with broadcast.subscribe(channel=channel) as subscriber:
            async for event in subscriber:
                yield Message(**json.loads(event.message))


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "World"

class AuthGraphQLWSHandler(GraphQLWSHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.authToken: Optional[str] = None

    async def handle_connection_init(self, message: OperationMessage) -> None:
        connection_params = message["payload"]
        self.token = connection_params.get("authToken")
        # print("token during connection init ",self.token)
        await super().handle_connection_init(message)

    async def get_context(self):
        context = await super().get_context()
        context["authToken"] = self.token
        return context


class AuthGraphQLRouter(GraphQLRouter):
    graphql_ws_handler_class = AuthGraphQLWSHandler


schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)
graphql_app = AuthGraphQLRouter(schema, graphiql=True)

