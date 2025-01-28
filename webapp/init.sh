#! /bin/sh

virtualenv .photo-webapp
. .photo-webapp/bin/activate

pip install -r requirements.txt

uvicorn backend:app --reload
