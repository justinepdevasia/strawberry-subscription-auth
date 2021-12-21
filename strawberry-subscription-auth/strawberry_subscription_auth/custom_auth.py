import typing
from strawberry.permission import BasePermission
from strawberry.types import Info


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

