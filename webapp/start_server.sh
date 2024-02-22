#! /bin/sh

. ../.photo/bin/activate
uvicorn backend:app --reload
