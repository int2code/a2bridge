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
    clang-format \
    gh 


RUN apt-get -y install git
RUN apt-get -y install dfu-util

# get the compiler - change below line to switch the STM version 
ARG ARM_GNU_VERSION=13.3.rel1
ARG ARM_GNU_TC=arm-gnu-toolchain-${ARM_GNU_VERSION}-x86_64-arm-none-eabi
ARG ARM_GNU_PATH=/opt/${ARM_GNU_TC}

RUN wget https://developer.arm.com/-/media/Files/downloads/gnu/13.3.rel1/binrel/${ARM_GNU_TC}.tar.xz && \
    tar -xf ${ARM_GNU_TC}.tar.xz -C /opt
RUN ls /opt/
RUN ls ${ARM_GNU_PATH}/bin
RUN ${ARM_GNU_PATH}/bin/arm-none-eabi-gcc --version
ENV PATH="$PATH:${ARM_GNU_PATH}/bin"
RUN arm-none-eabi-gcc --version

# get Protobufs protoc compiler
ARG PROTOC_VERSION=30.2
ARG PROTOC_FILE=protoc-${PROTOC_VERSION}-linux-x86_64
ARG PROTOC_PATH=/opt/protoc

RUN wget https://github.com/protocolbuffers/protobuf/releases/download/v${PROTOC_VERSION}/${PROTOC_FILE}.zip && \
    unzip ${PROTOC_FILE}.zip -d ${PROTOC_PATH}

ENV PATH="$PATH:${PROTOC_PATH}/bin"
RUN protoc --version

COPY ./requirements.txt ./
RUN pip3 install -r requirements.txt --break-system-packages

# ownership issue workaround to get git version during build
RUN git config --global --add safe.directory '*'


