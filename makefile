
THIS_MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

# Name of the shell script
DOCKER = /$(THIS_MAKEFILE_DIR)run.sh
TOOLS_DIR = $(THIS_MAKEFILE_DIR)tools
FMT_SCRIPT = $(TOOLS_DIR)/format/fmt.sh
PROTO_SCRIPT = $(TOOLS_DIR)/protobuf/generate.sh
DFU_UTIL = $(TOOLS_DIR)/dfu/dfu-util

# Default target
all: release debug

# Target to run the shell script
debug:
	@chmod +x $(DOCKER)
	@$(DOCKER) cmake -S . -B build/debug -G "Ninja" -DCMAKE_BUILD_TYPE=debug
	@$(DOCKER) cmake --build build/debug

local-debug:
	@cmake -S . -B build/local/debug -G "Ninja" -DCMAKE_BUILD_TYPE=debug
	@cmake --build build/local/debug

local-release:
	@chmod +x $(DOCKER)
	@cmake -S . -B build/local/release -G "Ninja" -DCMAKE_BUILD_TYPE=release
	@cmake --build build/local/release

release:
	@chmod +x $(DOCKER)
	@$(DOCKER) cmake -S . -B build/release -G "Ninja" -DCMAKE_BUILD_TYPE=release
	@$(DOCKER) cmake --build build/release

RelWithDebInfo:
	@chmod +x $(DOCKER)
	@$(DOCKER) cmake -S . -B build/release -G "Ninja" -DCMAKE_BUILD_TYPE=RelWithDebInfo
	@$(DOCKER) cmake --build build/release



flash-dfu-debug:
	$(DFU_UTIL) --download ./artifacts/a2bridge_debug_cm7.bin.dfu --reset

flash-dfu-release:
	$(DFU_UTIL) --download ./artifacts/a2bridge_release_cm7.bin.dfu --reset

generate-proto:
	@chmod +x $(DOCKER)
	@$(DOCKER) $(PROTO_SCRIPT)

# Clean target
clean:
	@rm -rfd build
	@echo "Build directory deleted."

.PHONY: all build clean format