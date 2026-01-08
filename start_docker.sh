#!/bin/bash
docker run --rm \
    -it \
    --volume=${PWD}:${PWD} \
    --workdir=${PWD} \
    --privileged \
    --user $(id -u):$(id -g) \
    stm32cubeclt \
    /bin/bash \