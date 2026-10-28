import asyncio
from fastapi import Request
from fastapi.responses import JSONResponse, Response


def register_media_routes(app, media):
    @app.post("/api/media")
    async def upload_audio(request: Request):
        audio = (
            await request.body()
        )  # ASGI and declared-length guards bound this to2MB.
        result = await asyncio.to_thread(
            media.upload,
            request.state.user,
            audio,
            request.headers.get("content-type", "").split(";")[0],
            consent=request.headers.get("x-saathi-media-consent") == "local-review",
        )
        return JSONResponse(result, status_code=201)

    @app.get("/api/media")
    def list_audio(request: Request):
        return media.list(request.state.user)

    @app.get("/api/media/{media_id}")
    def get_audio(media_id: str, request: Request):
        return media.get(request.state.user, media_id)

    @app.get("/api/media/{media_id}/content")
    def audio_content(media_id: str, request: Request):
        return Response(
            media.content(request.state.user, media_id),
            media_type="audio/wav",
            headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
        )

    @app.delete("/api/media/{media_id}")
    def delete_audio(media_id: str, request: Request):
        return media.delete(request.state.user, media_id)
