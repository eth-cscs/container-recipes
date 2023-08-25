FROM ubuntu:latest AS builder

ENV DEBIAN_FRONTEND noninteractive

ENV FORCE_UNSAFE_CONFIGURE 1

ENV PATH="/spack/bin:/apps/bin/:${PATH}"

ENV OPENMPI_VERSION=4.1.5

ENV MPICH_VERSION=4.1.1

ENV CMAKE_VERSION=3.26.4

RUN apt-get -y update && apt-get install -y apt-utils

# install basic tools
RUN apt-get install -y gcc g++ gfortran git make unzip file \
  vim wget pkg-config python3-pip curl tcl m4 cpio automake \
  apt-transport-https ca-certificates gnupg software-properties-common perl

# install CMake
RUN wget https://github.com/Kitware/CMake/releases/download/v${CMAKE_VERSION}/cmake-${CMAKE_VERSION}-linux-x86_64.tar.gz -O cmake.tar.gz && \
    tar zxvf cmake.tar.gz --strip-components=1 -C /usr > /dev/null

# get latest version of spack
RUN git clone https://github.com/spack/spack.git

# this is a temporarty fix until spack recipe is updated in the main repo
COPY ./spack /opt/spack
RUN spack repo add --scope system /opt/spack

# find all external packages
RUN spack external find --all --not-buildable -p /usr

ARG CUDA_ARCH=80

# set the location of packages built by spack
RUN spack config add config:install_tree:root:/opt/local
RUN spack config add packages:all:target:[zen2]
RUN spack config add packages:all:variants:cuda_arch=${CUDA_ARCH}

# find compilers
RUN spack compiler find

# end of common block

RUN spack env create -d /build-env  --with-view /apps
RUN spack -e /build-env add mpich@${MPICH_VERSION}
RUN spack -e /build-env add sirius@develop%gcc build_type=Release +cuda +fortran +tests +scalapack ^mpich@${MPICH_VERSION} ^openblas threads=openmp ^cuda@11.8

RUN spack -e /build-env concretize
RUN spack -e /build-env install

RUN spack clean --all

RUN echo $(spack find --format='{prefix.lib}' libfabric) > /etc/ld.so.conf.d/libfabric.conf
RUN ldconfig
