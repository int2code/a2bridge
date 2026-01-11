#!/bin/bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

docker build --progress=plain -t stm32cubeclt $SCRIPT_DIR/tools/