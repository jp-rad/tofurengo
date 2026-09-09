from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from api import api
from config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name)

# Static files (CSS, JS, fonts, index.html)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Vendor JS files (tofurengo-js)
app.mount("/vendor/tofurengo", StaticFiles(directory="../tofurengo_js/dist"), name="vendor_tofurengo")

# UI entry point
@app.get("/console", include_in_schema=False)
def console():
    return FileResponse("static/index.html")

# Existing API router
app.include_router(api.api_router)


def serve():
    uvicorn.run(app, port=settings.app_port, host=settings.app_host)


if __name__ == "__main__":
    serve()
