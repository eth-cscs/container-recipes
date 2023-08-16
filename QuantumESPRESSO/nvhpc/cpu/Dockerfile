FROM ubuntu:latest AS builder

ENV DEBIAN_FRONTEND noninteractive

ENV FORCE_UNSAFE_CONFIGURE 1

ENV PATH="/spack/bin:/apps/bin/:${PATH}"

ENV OPENMPI_VERSION=4.1.5

ENV MPICH_VERSION=4.1.1

ENV CMAKE_VERSION=3.26.3

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

# find all external packages
RUN spack external find --all --not-buildable -p /usr

ARG CUDA_ARCH=80

# set the location of packages built by spack
RUN spack config add config:install_tree:root:/opt/local
RUN spack config add packages:all:variants:cuda_arch=${CUDA_ARCH}

# find compilers
RUN spack compiler find

ARG NVHPC_VERSION=22.11

# install nvhpc
RUN spack install nvhpc@${NVHPC_VERSION} %gcc

# add nvhpc compiler
RUN spack compiler find $(spack location -i nvhpc)/Linux_x86_64/${NVHPC_VERSION}/compilers

ARG QE_VERSION=qe-7.1

RUN wget https://gitlab.com/QEF/q-e/-/archive/${QE_VERSION}/q-e-${QE_VERSION}.tar.gz && \
    tar zxvf q-e-${QE_VERSION}.tar.gz

RUN spack env create -d /build-env  --with-view /apps
#RUN spack -e /build-env add openmpi@${OPENMPI_VERSION} %nvhpc fabrics=ofi schedulers=slurm ^libiconv%gcc ^slurm%gcc
RUN spack -e /build-env add mpich@${MPICH_VERSION} %nvhpc ^libiconv%gcc ^libfabric%gcc
RUN spack -e /build-env add libxc@5.2.3 %nvhpc
#RUN spack -e /build-env add quantum-espresso@develop %nvhpc +libxc ~scalapack +openmp ^openmpi ^openblas threads=openmp
RUN spack -e /build-env add quantum-espresso@develop %nvhpc ~cuda +libxc ~scalapack +openmp ^mpich ^openblas threads=openmp
RUN spack -e /build-env develop -p /q-e-${QE_VERSION} quantum-espresso@develop

RUN spack -e /build-env concretize
RUN spack -e /build-env install

RUN spack clean --all

RUN echo $(spack find --format='{prefix.lib}' libfabric) > /etc/ld.so.conf.d/libfabric.conf
#RUN echo $(spack find --format='{prefix.lib}' mpich) > /etc/ld.so.conf.d/mpich.conf
RUN ldconfig
