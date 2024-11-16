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
    allow_methods=["*"],
    allow_headers=["*"],
)


image_formats = (".jpg", ".jpeg", ".png", ".svg")
base_dir = ""


class ImagesList(pydantic.BaseModel):
    images: typing.List[str]


class SaveSortedImages(pydantic.BaseModel):
    directory: str
    name: str
    sorted_images: ImagesList


@app.get("/list_images/")
def list_images(directory: str, sort_by_exif_date: bool = False) -> ImagesList:
    images = [
        os.path.join(subdir, file) for subdir, dirs, files in os.walk(directory) for file in files if file.lower().endswith(image_formats)
    ]
    return ImagesList(images=sorted(images))


def get_sorted_images_filename(directory: str, name: str) -> str:
    return os.path.join(directory, name+".json")


@app.get("/sorted_images/")
def load_sorted_images(directory: str, name: str) -> ImagesList:
    sorted_images_filename = get_sorted_images_filename(directory=directory, name=name)
    sorted_images = None
    if os.path.exists(sorted_images_filename):
        with open(sorted_images_filename) as sorted_images_file:
            sorted_images = ImagesList(**json.load(sorted_images_file))
    else:
        sorted_images = ImagesList(images=[])
    return sorted_images


@app.post("/sorted_images/")
def save_sorted_images(body: SaveSortedImages) -> str:
    sorted_images_filename = get_sorted_images_filename(directory=body.directory, name=body.name)
    with open(sorted_images_filename, "w") as sorted_images_file:
        json.dump(body.sorted_images.dict(), sorted_images_file, indent=4)
    return sorted_images_filename
