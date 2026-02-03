#!/bin/bash
set -e

echo "Generate proto files"
cd tools/protobuf
protoc --python_out=python interface.proto --experimental_allow_proto3_optional
python3 nanopb/generator/nanopb_generator.py interface.proto -D ../../CM7/protobuf_gen
