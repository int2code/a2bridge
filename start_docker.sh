#!/bin/bash

set -e


if command -v gh >/dev/null 2>&1; then
    export GITHUB_TOKEN="$(gh auth token)"
else
    export GITHUB_TOKEN="invalidtoken"
fi

export GITHUB_TOKEN="$(gh auth token)"

docker run --rm \
    -e GITHUB_TOKEN \
    -it \
    --volume=${PWD}:${PWD} \
    --workdir=${PWD} \
    --privileged \
    --user $(id -u):$(id -g) \
    stm32cubeclt \
    /bin/bash \