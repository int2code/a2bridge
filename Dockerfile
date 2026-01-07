FROM ubuntu:24.04


RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get -y install \
    cmake \
    ninja-build \
    unzip \
    patch \
    wget \
    xz-utils \
    python3 \
    python3-pip \
    curl \
    clang-format


RUN apt-get -y install git
RUN apt-get -y install dfu-util

# get the compiler
RUN wget https://developer.arm.com/-/media/Files/downloads/gnu/13.3.rel1/binrel/arm-gnu-toolchain-13.3.rel1-x86_64-arm-none-eabi.tar.xz
RUN tar -xf arm-gnu-toolchain-13.3.rel1-x86_64-arm-none-eabi.tar.xz
ENV PATH $PATH:$PWD/arm-gnu-toolchain-13.3.rel1-x86_64-arm-none-eabi/bin
RUN arm-none-eabi-gcc --version

# get protoc compiler
RUN wget https://github.com/protocolbuffers/protobuf/releases/download/v30.2/protoc-30.2-linux-x86_64.zip
RUN unzip protoc-30.2-linux-x86_64.zip -d protoc
ENV PATH $PATH:$PWD/protoc/bin
RUN protoc --version

COPY ./requirements.txt ./
RUN pip3 install -r requirements.txt --break-system-packages

# ownership issue workaround to get git version during build
RUN git config --global --add safe.directory '*'


