from starlette.exceptions import HTTPException


class BodyLimit:
    """Count received bytes even when Content-Length is absent/chunked."""

    def __init__(self, app, maximum=60000):
        self.app, self.maximum = app, maximum

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        size = 0

        async def limited():
            nonlocal size
            message = await receive()
            if message["type"] == "http.request":
                size += len(message.get("body", b""))
                if size > self.maximum:
                    raise HTTPException(413, "Request exceeds60KB.")
            return message

        return await self.app(scope, limited, send)
