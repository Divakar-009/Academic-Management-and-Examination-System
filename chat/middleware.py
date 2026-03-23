import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from channels.middleware import BaseMiddleware
from urllib.parse import parse_qs
from asgiref.sync import sync_to_async

User = get_user_model()


class JWTAuthMiddleware(BaseMiddleware):

    async def __call__(self, scope, receive, send):

        query_string = scope["query_string"].decode()
        query_params = parse_qs(query_string)

        token = query_params.get("token")

        if token:
            token = token[0]
            try:
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=["HS256"]
                )

                user = await sync_to_async(User.objects.get)(
                    id=payload["user_id"]
                )

                scope["user"] = user

            except Exception as e:
                print("JWT ERROR:", e)
                scope["user"] = None
        else:
            scope["user"] = None

        return await super().__call__(scope, receive, send)