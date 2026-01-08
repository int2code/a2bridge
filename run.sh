#!/bin/bash
docker run --rm \
    --volume=${PWD}:${PWD} \
    --workdir=${PWD} \
    --privileged \
    --user $(id -u):$(id -g) \
    stm32cubeclt \
    $@
