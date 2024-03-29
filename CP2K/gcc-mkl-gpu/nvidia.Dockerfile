FROM docker.io/nvidia/cuda:12.1.0-devel-ubuntu22.04 as builder

# Setup CUDA environment.
ENV CUDA_PATH /usr/local/cuda
ENV LD_LIBRARY_PATH /usr/local/cuda/lib64
ARG CUDA_ARCH=80

ENV DEBIAN_FRONTEND noninteractive

ENV FORCE_UNSAFE_CONFIGURE 1

ENV PATH="/spack/bin:${PATH}"
ENV LIBRARY_PATH=$LIBRARY_PATH:/usr/local/cuda/lib64/stubs
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
RUN ln -s /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/stubs/libcuda.so.1

# for the MPI hook
RUN echo $(spack find --format='{prefix.lib}' mpich) > /etc/ld.so.conf.d/mpich.conf
RUN ldconfig

# no need to use spla offloading on cpu only version
ENV SPACK_ROOT=/spack 
ENV SPEC_MKL="cp2k@master%gcc build_system=cmake build_type=Release ~libint smm=libxsmm +spglib +cosma +mpi +openmp +cuda cuda_arch=${CUDA_ARCH} ^intel-oneapi-mkl+cluster ^cosma+scalapack+shared+cuda~apps~tests ^mpich@${MPICH_VERSION} ^dbcsr@develop+cuda~shared cuda_arch=70"

# install all dependencies
RUN spack env create -d /opt/cp2k-nvidia-gpu
RUN spack -e /opt/cp2k-nvidia-gpu  add $SPEC_MKL 
RUN spack -e /opt/cp2k-nvidia-gpu install --only=dependencies --fail-fast $SPEC_MKL
RUN spack --color always -e /opt/cp2k-nvidia-gpu dev-build -q --source-path /cp2k $SPEC_MKL
