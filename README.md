
# A2Bridge

This is the A2Bridge SDK project. You can use it to develop and run your own code on the A2Bridge hardware or just build 
the latest A2Bridge software. 

If you want to experience more about how to use A2Bridge please refer to our [User Guide](https://int2code.github.io/a2bridge/)

If you want to order A2Bridge hardware please contact us at: sales@int2code.com 


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
Beside that you should install all the tools installed in the container above. 

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

### Build results 

You can find the build results in artifacts directory.

## Flash the A2Bridge 

### Using DFU 

You can flash the A2Bridge with the new build SW using following command

```bash 
dfu-util --download artifacts/a2bridge_release_cm7.bin.dfu --reset
```

***ATTENTION***: It is known problem that the DFU 
