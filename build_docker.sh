#!/bin/bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

docker build -f $SCRIPT_DIR/tools/Dockerfile -t stm32cubeclt $SCRIPT_DIR