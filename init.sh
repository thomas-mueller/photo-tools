#! /bin/sh

export PHOTO_TOOLS=`dirname $(readlink -f $0)`

export PATH="${PHOTO_TOOLS}:${PATH}"
export PYTHONPATH="${PHOTO_TOOLS}:${PYTHONPATH}"

