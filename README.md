<!-- TOC -->
- [A2Bridge](#a2bridge)
  - [Clone and build](#clone-and-build)
    - [Clone the repo](#clone-the-repo)
    - [Docker](#docker)
    - [Build on local machine](#build-on-local-machine)
    - [Compile the A2Bridge software](#compile-the-a2bridge-software)
    - [Selecting A2Bridge core library version ](#selecting-a2bridge-core-library-version)
    - [Build results](#build-results)
  - [Flash the A2Bridge](#flash-the-a2bridge)
    - [Using DFU](#using-dfu)
  - [Write your own code](#flash-the-a2bridge)
<!-- /TOC -->

# A2Bridge

This is the A2Bridge SDK project. You can use it to develop and run your own code on the A2Bridge hardware or just build 
the latest A2Bridge software. 

If you want to experience more about how to use A2Bridge please refer to our [User Guide](https://int2code.github.io/a2bridge/)

If you want to order A2Bridge hardware please visit [A2Bridge shop](https://a2bridge.int2code.com/)


## Clone and build 

The build works only under Linux or WSL. 

### Clone the repo 

Clone using you ssh key 

```bash
git clone git@github.com:int2code/a2bridge.git
cd a2bridge
```


### Docker 
By default the project is setup to be build in the docker container.

### Install and configure docker:

```bash
sudo apt-get install docker.io
sudo groupadd docker
sudo usermod -aG docker ${USER}
```

***NOTE***: restart WSL afterwards

Check if the docker works correctly: 
```bash
docker run hello-world
```

#### Build docker container 

To build the container call:
```bash
./build_docker.sh 
```
#### Run command in docker 

You can run CMake or other commands in the docker using the 
```bash
./run.sh <your command>
```

or start the docker container in interactive mode 
```bash
./start_docker.sh
```

### Build on local machine  

You can compile and build the project also on you local workstation without docker container.
For that you should install the corresponding version of the STM32CubeCLT from https://www.st.com/en/development-tools/stm32cubeclt.html 
The version which shall be used can be find in the [Docker file](tools/Dockerfile)
Beside that, you should install all the tools installed in the container above. 

### Compile the A2Bridge software 

#### Using make 

To compile the project you can use helper makefile targets. 
Just call one of the targets:

`make` - builds in docker both debug and release target \
`make release` - builds in docker release target only \
`make local-release` - builds release target using your locally installed build environment \
`make debug` - builds in docker debug target only \
`make local-debug` - builds debug target using your locally installed build environment \
`make clean` - cleanup all builds (local and docker) \
`make format` - formats source code \
`make flash-dfu-debug` - flashes debug image via DFU \
`make flash-dfu-release` - flashes release image via DFU \
`make generate-proto` - generates new protobuf files


You can compile docker targets (debug, release) without need to install locally the STM32 development tools. 
Docker build targets are also used to build CI/CD artifacts. 

#### Using CMake 

You can compile the project also using directly the CMake commands - please check [makefile](./makefile) for more details

***ATTENTION***: Docker builds are done in the `build/debug` and `build/release`. Mixing the locations with local builds will lead to errors. 


### Selecting A2Bridge core library version 

By default the build will try to fetch the core library corresponding to the version which your repo based on (the last seen tag in your tree will decide about the version).
But if you want to use another version, or you have stared your own project base on this repo and there is no tag in your history corresponding to th A2Bridge core library version, you will have to fix the version by hand. For that edit the main [CMakeLists.txt](CMakeLists.txt) in following way (setting the version to v3.0.2 release):

```cmake
set(A2BRIDGE_CORE_VERSION "3.0.2" CACHE  STRING  "A2Bridge core lib version")
set(A2BRIDGE_VERSION_DEV 0 CACHE BOOL "A2Bridge core dev version flag")
```

### Build results 

You can find the build results in artifacts directory.

## Flash the A2Bridge 

### Using DFU 

You can flash the A2Bridge with the new build SW using following command

```bash 
dfu-util --download artifacts/a2bridge_release_cm7.bin.dfu --reset
```

For more information please refer to [UserGuide/Firmware Update](https://int2code.github.io/a2bridge/dfu/)


## Write your own code 

The best place to start with your own code for A2Bridge is to use the example code prepared under [SdkExampleTasks.c](src/SdkExampleTasks.c)
Basic information:
- the SDK API can be found in Sdk.h after the a2bridge library has been installed in your build directory (usually under `./build/release/_deps/a2bridge_core/2.4.4/release/extract/a2bridge_core/include/Sdk.h`)
- you can add up to 5 custom tasks for your application 
- the A2Bridge is using the FreeRTOS, currently the full API of it is public in the core library and can be used (carefully ;-) ) 
- the SDK is still under development and the API function set is open, if you need anything which is not available yet, please contact us directly at info@int2code.com 