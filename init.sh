#! /bin/sh

export PHOTO_TOOLS=$(readlink -e `dirname $BASH_SOURCE`)

export PATH="${PHOTO_TOOLS}:${PATH}"
export PYTHONPATH="${PHOTO_TOOLS}:${PYTHONPATH}"

