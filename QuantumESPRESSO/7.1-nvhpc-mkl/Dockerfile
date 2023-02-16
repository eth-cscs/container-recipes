FROM nvcr.io/nvidia/nvhpc:22.11-devel-cuda_multi-ubuntu22.04 as builder

ENV DEBIAN_FRONTEND noninteractive

ENV FORCE_UNSAFE_CONFIGURE 1

ENV PATH="/spack/bin:${PATH}"

ENV SPEC="quantum-espresso%nvhpc +libxc +scalapack +openmp +cuda ^mpich ^intel-oneapi-mkl+cluster"

ENV MPICH_VERSION=3.4.3

ENV CMAKE_VERSION=3.25.2

RUN apt-get -y update

RUN apt-get install -y apt-utils

# install basic tools
RUN apt-get install -y gcc g++ gfortran git make unzip file \
  vim wget pkg-config python3-pip curl tcl m4 cpio automake \
  apt-transport-https ca-certificates gnupg software-properties-common perl

# install CMake
RUN wget https://github.com/Kitware/CMake/releases/download/v${CMAKE_VERSION}/cmake-${CMAKE_VERSION}-linux-x86_64.tar.gz -O cmake.tar.gz && \
    tar zxvf cmake.tar.gz --strip-components=1 -C /usr

# get latest version of spack
RUN git clone https://github.com/spack/spack.git

# set the location of packages built by spack
RUN spack config add config:install_tree:root:/opt/local

# find all external packages
RUN spack external find --all --not-buildable

# find compilers
RUN spack compiler find

# explicitly ask for nvhpc installation
RUN spack install libxc%nvhpc

RUN spack install --only=dependencies mpich@${MPICH_VERSION} %nvhpc
RUN spack install mpich@${MPICH_VERSION} %nvhpc
RUN echo $(spack find --format='{prefix.lib}' mpich) > /etc/ld.so.conf.d/mpich.conf

# show spec
RUN spack spec $SPEC

RUN spack install --only=dependencies $SPEC

RUN wget https://gitlab.com/QEF/q-e/-/archive/qe-7.1/q-e-qe-7.1.tar.gz && \
    tar zxvf q-e-qe-7.1.tar.gz

# build CPU
RUN cd /q-e-qe-7.1 && mkdir build-cpu && cd build-cpu &&\
    spack build-env $SPEC -- cmake .. -DCMAKE_INSTALL_RPATH_USE_LINK_PATH=ON -DQE_ENABLE_OPENMP=1 -DQE_ENABLE_SCALAPACK=1 -DQE_ENABLE_LIBXC=1 -DCMAKE_INSTALL_PREFIX=/opt/local/qe-cpu &&\
    spack build-env $SPEC -- make -j install

# build GPU
RUN cd /q-e-qe-7.1 && mkdir build-gpu && cd build-gpu &&\
    spack build-env $SPEC -- cmake .. -DCMAKE_INSTALL_RPATH_USE_LINK_PATH=ON -DQE_ENABLE_OPENMP=1 -DQE_ENABLE_SCALAPACK=0 -DQE_ENABLE_LIBXC=1 -DQE_ENABLE_CUDA=1 -DCMAKE_INSTALL_PREFIX=/opt/local/qe-gpu &&\
    spack build-env $SPEC -- make -j install

RUN mkdir stage-copy
# use ldd to find all shared libraries of a binary (ldd ...)
# extract the full path of the *so files (grep -o ...)
# copy (cp --parent ...) with the directory structure into /stage-copy directory
RUN ldd /opt/local/qe-gpu/bin/pw.x | grep -o '/[-a-zA-Z0-9_/\.]*\.so[\.0-9]*' | xargs -I{} cp --parent {} stage-copy
RUN ldd /opt/local/qe-cpu/bin/pw.x | grep -o '/[-a-zA-Z0-9_/\.]*\.so[\.0-9]*' | xargs -I{} cp --parent {} stage-copy
# MKL requires special care
RUN cp --parent $(spack find --format='{prefix}/mkl/{version}/lib/intel64/libmkl_def.so.2' intel-oneapi-mkl) stage-copy

# Bare OS image to run the installed executables
#FROM nvcr.io/nvidia/nvhpc:22.11-runtime-cuda11.8-ubuntu22.04
FROM ubuntu:22.04
RUN apt-get -y update
RUN apt-get install -y apt-utils

COPY --from=builder /opt/local/qe-gpu/bin/pw.x /qe-gpu/pw.x
COPY --from=builder /opt/local/qe-cpu/bin/pw.x /qe-cpu/pw.x

# copy only necessary *.so libraries, required by the application
COPY --from=builder /stage-copy/opt /opt
COPY --from=builder /stage-copy/lib /usr/lib

# For the sarus mpi hook
COPY --from=builder /etc/ld.so.conf.d/mpich.conf /etc/ld.so.conf.d/mpich.conf
RUN ldconfig
