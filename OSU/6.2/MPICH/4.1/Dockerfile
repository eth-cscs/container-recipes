FROM docker.io/library/ubuntu:22.04

ARG libfabric_version=1.14.1
ARG mpi_version=4.1
ARG mpi_short_version=4.1
ARG osu_version=6.2

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
       apt-get install -y --no-install-recommends \
         build-essential \
         ca-certificates \
         automake \
         autoconf \
         libtool \
         make \
         gdb \
         strace \
         wget \
         python3 \
    && rm -rf /var/lib/apt/lists/*

# Install libfabric
RUN wget -q https://github.com/ofiwg/libfabric/archive/v${libfabric_version}.tar.gz \
    && tar xf v${libfabric_version}.tar.gz \
    && cd libfabric-${libfabric_version} \
    && ./autogen.sh \
    && ./configure --prefix=/usr \
    && make -j$(nproc) \
    && make install \
    && ldconfig \
    && cd .. \
    && rm -rf v${libfabric_version}.tar.gz libfabric-${libfabric_version}

# Install MPICH
RUN wget -q https://www.mpich.org/static/downloads/${mpi_version}/mpich-${mpi_version}.tar.gz \
    && tar xf mpich-${mpi_version}.tar.gz \
    && cd mpich-${mpi_version} \
    && ./autogen.sh \
    && ./configure --disable-fortran --enable-fast=all,O3 --prefix=/usr \
           --with-device=ch4:ofi --with-libfabric=/usr \
    && make -j$(nproc) \
    && make install \
    && ldconfig \
    && cd .. \
    && rm -rf mpich-${mpi_version}.tar.gz mpich-${mpi_version}

# Install OSU Micro-benchmarks
RUN wget -q http://mvapich.cse.ohio-state.edu/download/mvapich/osu-micro-benchmarks-${osu_version}.tar.gz \
    && tar xf osu-micro-benchmarks-${osu_version}.tar.gz \
    && cd osu-micro-benchmarks-${osu_version} \
    && ./configure --prefix=/usr/local CC=$(which mpicc) CFLAGS=-O3 \
    && make -j$(nproc) \
    && make install \
    && cd .. \
    && rm -rf osu-micro-benchmarks-${osu_version} osu-micro-benchmarks-${osu_version}.tar.gz

# Add the location of the get_local_rank utility to PATH
ENV PATH=/usr/local/libexec/osu-micro-benchmarks:$PATH

WORKDIR /usr/local/libexec/osu-micro-benchmarks/mpi/pt2pt

