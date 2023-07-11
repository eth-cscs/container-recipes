FROM ubuntu:latest AS builder
#FROM nvcr.io/nvidia/nvhpc:23.1-runtime-cuda11.8-ubuntu22.04
#FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND noninteractive

ENV FORCE_UNSAFE_CONFIGURE 1

ENV PATH="/spack/bin:${PATH}"

ENV OPENMPI_VERSION=4.1.5

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

# set the location of packages built by spack
RUN spack config add config:install_tree:root:/opt/local

# find all external packages
RUN spack external find --all --not-buildable -p /usr

# find compilers
RUN spack compiler find

RUN spack install nvhpc@23.1 %gcc

RUN spack compiler find $(spack location -i nvhpc)/Linux_x86_64/2023/compilers

ARG QE_VERSION=qe-7.1

RUN wget https://gitlab.com/QEF/q-e/-/archive/${QE_VERSION}/q-e-${QE_VERSION}.tar.gz && \
    tar zxvf q-e-${QE_VERSION}.tar.gz

RUN spack env create -d /qe-build-env  --with-view /qe
RUN spack -e /qe-build-env add openmpi@4.1.5 %nvhpc fabrics=ofi ^libiconv%gcc
RUN spack -e /qe-build-env add libxc@5.2.3 %nvhpc
RUN spack -e /qe-build-env add quantum-espresso@develop %nvhpc +libxc ~scalapack +openmp ~cuda ^openmpi ^openblas threads=openmp ^cuda@11.8 ^openmpi
RUN spack -e /qe-build-env develop -p /q-e-${QE_VERSION} quantum-espresso@develop

RUN spack -e ./qe-build-env concretize
RUN spack -e ./qe-build-env install


##==# build CPU
##==#RUN cd /q-e-${QE_VERSION} && mkdir build-cpu && cd build-cpu &&\
##==#    spack build-env $SPEC -- cmake .. -DCMAKE_INSTALL_RPATH_USE_LINK_PATH=ON -DQE_ENABLE_OPENMP=1 -DQE_ENABLE_SCALAPACK=1 -DQE_ENABLE_LIBXC=1 -DCMAKE_INSTALL_PREFIX=/opt/local/qe-cpu &&\
##==#    spack build-env $SPEC -- make -j install
#
## build GPU
#RUN cd /q-e-${QE_VERSION} && mkdir build-gpu && cd build-gpu &&\
#    spack build-env $SPEC -- cmake .. -DCMAKE_INSTALL_RPATH_USE_LINK_PATH=ON -DQE_ENABLE_OPENMP=1 -DQE_ENABLE_SCALAPACK=0 -DQE_ENABLE_LIBXC=1 -DQE_ENABLE_CUDA=1 -DCMAKE_INSTALL_PREFIX=/opt/local/qe-gpu &&\
#    spack build-env $SPEC -- make -j install
#
#== ##==RUN echo $(spack find --format='{prefix.lib}' libfabric) > /etc/ld.so.conf.d/mpi.conf
#== ##==
RUN mkdir -p /qe1/bin
RUN cp -r -l /qe/bin/* /qe1/bin/

RUN mkdir stage-copy
# use ldd to find all shared libraries of a binary (ldd ...)
# extract the full path of the *so files (grep -o ...)
# copy (cp --parent ...) with the directory structure into /stage-copy directory
#   RUN ldd /opt/local/qe-gpu/bin/pw.x | grep -o '/[-a-zA-Z0-9_/\.]*\.so[\.0-9]*' | xargs -I{} cp --parent {} stage-copy
RUN ldd /qe1/bin/pw.x | grep -o '/[-a-zA-Z0-9_/\.]*\.so[\.0-9]*' | xargs -I{} cp --parent {} stage-copy
# MKL requires special care
#RUN cp --parent $(spack find --format='{prefix}/mkl/{version}/lib/intel64/libmkl_def.so.2' intel-oneapi-mkl) stage-copy

# Bare OS image to run the installed executables
#FROM nvcr.io/nvidia/nvhpc:22.11-runtime-cuda11.8-ubuntu22.04
FROM ubuntu:22.04
RUN apt-get -y update
RUN apt-get install -y apt-utils

COPY --from=builder /qe1 /qe
##==#   #COPY --from=builder /opt/local/qe-cpu /opt/local/qe-cpu
##==#   
##==#   # copy only necessary *.so libraries, required by the application
COPY --from=builder /stage-copy/opt /opt
COPY --from=builder /stage-copy/lib /usr/lib
#== #== ##==#   
#== #== ##==#   # For the sarus mpi hook
#== #== ##==#   COPY --from=builder /etc/ld.so.conf.d/mpi.conf /etc/ld.so.conf.d/mpi.conf
#== #== ##==#   RUN ldconfig
