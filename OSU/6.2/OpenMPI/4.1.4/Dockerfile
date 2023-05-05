FROM docker.io/ubuntu:22.04

ARG libfabric_version=1.14.1
ARG mpi_version=4.1.4
ARG mpi_short_version=4.1
ARG osu_version=6.2

RUN apt-get update && apt-get install -y \
        build-essential \
        ca-certificates \
        automake \
        autoconf \
        libtool \
        libpmi2-0-dev \
        gdb \
        strace \
        wget \
        git \
        --no-install-recommends \
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

# Install OpenMPI 4.1.4 using libfabric libraries
RUN wget -q  https://download.open-mpi.org/release/open-mpi/v${mpi_short_version}/openmpi-${mpi_version}.tar.gz \
    && tar xf openmpi-${mpi_version}.tar.gz \
    && cd openmpi-${mpi_version} \
    && ./configure --with-libfabric=/usr --prefix=/usr \
       --with-pmi=/usr/include/slurm --with-pmi-libdir=/usr/lib/x86_64-linux-gnu \
       CFLAGS="-I/usr/include/slurm" \
    && make -j$(nproc) \
    && make install \
    && ldconfig \
    && cd .. \
    && rm -rf openmpi-${mpi_version}.tar.gz openmpi-${mpi_version}

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

WORKDIR /usr/local/libexec/osu-micro-benchmarks/mpi

