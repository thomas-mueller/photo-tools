import fastapi
import fastapi.middleware.cors
import json
import pydantic
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
base_dir = ""


class ImagesList(pydantic.BaseModel):
    images: typing.List[str]


class SortedImagesConfiguration(pydantic.BaseModel):
    image_directories: typing.List[str]
    sorted_images: typing.List[str]
    path: str


@app.get("/list_images/")
def list_images(directory: str, sort_by_exif_date: bool = False) -> ImagesList:
    images = [
        os.path.join(subdir, file) for subdir, dirs, files in os.walk(directory) for file in files if file.lower().endswith(image_formats)
    ]
    return ImagesList(images=sorted(images))


@app.get("/sorted_images_configuration/")
def load_sorted_images_configuration(path: str) -> SortedImagesConfiguration:
    if not os.path.isabs(path):
        path = os.path.join(base_dir, path)
    config = None
    with open(path) as input_file:
        config = json.load(input_file)
    return SortedImagesConfiguration(**config)


@app.post("/sorted_images_configuration/")
def save_sorted_images_configuration(config: SortedImagesConfiguration):
    if not os.path.isabs(config.path):
        config.path = os.path.join(base_dir, config.path)
    with open(config.path, "w") as output_file:
        json.dump(config, output_file, indent=4)
