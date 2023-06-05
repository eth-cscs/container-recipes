FROM ubuntu:23.04 as builder

ARG CUDA_ARCH=80

ENV DEBIAN_FRONTEND noninteractive

ENV FORCE_UNSAFE_CONFIGURE 1

ENV PATH="/spack/bin:${PATH}"

ENV MPICH_VERSION=4.0.3
ENV CMAKE_VERSION=3.25.2
RUN apt-get update -qq
RUN apt-get install -qq --no-install-recommends autoconf autogen automake autotools-dev bzip2 ca-certificates g++ gcc gfortran git less libtool libtool-bin make nano patch pkg-config python3 unzip wget xxd zlib1g-dev cmake gnupg m4 xz-utils libssl-dev libssh-dev 
RUN wget -qO /usr/local/bin/yq https://github.com/mikefarah/yq/releases/latest/download/yq_linux_386 && chmod a+x /usr/local/bin/yq
# get latest version of spack
RUN git clone https://github.com/spack/spack.git
RUN git clone https://github.com/eth-cscs/cp2k.git
RUN cd cp2k && git checkout cicd && cd ..

# set the location of packages built by spack
RUN spack config add config:install_tree:root:/opt/spack
# set cuda_arch for all packages
# RUN spack config add packages:all:variants:cuda_arch=${CUDA_ARCH}

# find all external packages
RUN spack external find --all --exclude python
# find compilers
RUN spack compiler find
# tweaking the arguments
RUN yq -i '.compilers[0].compiler.flags.fflags = "-fallow-argument-mismatch"' /root/.spack/linux/compilers.yaml

# copy bunch of things from the ci
RUN ls -lap /cp2k/ci 
RUN cp -r /cp2k/ci/spack /root/spack-recipe
RUN spack repo add /root/spack-recipe/ --scope user

# for the MPI hook
RUN echo $(spack find --format='{prefix.lib}' mpich) > /etc/ld.so.conf.d/mpich.conf
RUN ldconfig

# no need to use spla offloading on cpu only version
ENV SPACK_ROOT=/spack 
ENV SPEC_MKL="cp2k@master%gcc build_system=cmake build_type=Release +sirius +elpa +libxc +libint smm=libxsmm +spglib +cosma +mpi +openmp ^intel-oneapi-mkl+cluster ^cosma+scalapack+shared ^mpich@${MPICH_VERSION}"

# install all dependencies
RUN spack env create -d /opt/cp2k-cpu
RUN spack -e /opt/cp2k-cpu  add $SPEC_MKL 
RUN spack -e /opt/cp2k-cpu install --only=dependencies --fail-fast $SPEC_MKL
RUN spack --color always -e /opt/cp2k-cpu dev-build -q --source-path /cp2k $SPEC_MKL
