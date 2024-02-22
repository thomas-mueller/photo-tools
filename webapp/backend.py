import fastapi
import fastapi.middleware.cors
import os
import typing

app = fastapi.FastAPI()

# Set up CORS middleware
app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


image_formats = (".jpg", ".jpeg", ".png", ".svg")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/list_images/")
def list_images(directory: str):
    return {
        "images": sorted(
            [
                os.path.join(subdir, file)
                for subdir, dirs, files in os.walk(directory)
                for file in files
                if file.lower().endswith(image_formats)
            ]
        )
    }
