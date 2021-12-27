import typing
from strawberry.permission import BasePermission
from strawberry.types import Info
from strawberry.fastapi import GraphQLRouter
from strawberry.fastapi.handlers import GraphQLWSHandler
from strawberry.subscriptions.protocols.graphql_ws.types import OperationMessage


# just checking if authToken starts with "token"
# can customize accordingly
async def authenticate_token(token: str) -> bool:
    return token[:5] == "token"


class IsAuthenticated(BasePermission):
    message = "User is not authenticated"


    def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:
        authToken: str = info.context.get("authToken")
        if authToken:
            return authenticate_token(authToken)

        return False
    

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

