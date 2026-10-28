from starlette.exceptions import HTTPException


class BodyLimit:
    """Count received bytes even when Content-Length is absent/chunked."""

    def __init__(self, app, maximum=60000, limits_by_path=None):
        self.app, self.maximum = app, maximum
        self.limits_by_path = limits_by_path or {}

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        size = 0
        maximum = (
            self.limits_by_path.get(scope.get("path"), self.maximum)
            if scope.get("method") == "POST"
            else self.maximum
        )

        async def limited():
            nonlocal size
            message = await receive()
            if message["type"] == "http.request":
                size += len(message.get("body", b""))
                if size > maximum:
                    raise HTTPException(413, "Request exceeds the allowed byte limit.")
            return message

        return await self.app(scope, limited, send)
