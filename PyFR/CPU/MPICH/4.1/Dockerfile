FROM docker.io/ubuntu:22.04

LABEL com.pyfr.version="1.15.0"

# Install system dependencies
RUN apt-get update && apt-get install -y   \
        unzip                       \
        git                         \
        wget                        \
        build-essential             \
        automake                    \
        autoconf                    \
        libtool                     \
        strace                      \
        libopenblas-dev             \
        liblapack-dev               \
        libpmi2-0-dev               \
        python3-dev                 \
        python3-pip                 \
        libhdf5-dev                 \
		libmetis-dev				\
        --no-install-recommends  && \
    rm -rf /var/lib/apt/lists/*

# Install libfabric
ARG libfabric_version=1.14.1
RUN wget -q https://github.com/ofiwg/libfabric/archive/v${libfabric_version}.tar.gz \
    && tar xf v${libfabric_version}.tar.gz \
    && cd libfabric-${libfabric_version} \
    && ./autogen.sh \
    && ./configure --prefix=/usr --enable-efa=no \
    && make -j$(nproc) \
    && make install \
    && ldconfig \
    && cd .. \
    && rm -rf v${libfabric_version}.tar.gz libfabric-${libfabric_version}

# Install MPICH
RUN wget -q https://www.mpich.org/static/downloads/4.1/mpich-4.1.tar.gz \
    && tar xf mpich-4.1.tar.gz \
    && cd mpich-4.1 \
    && ./autogen.sh \
    && ./configure --disable-fortran --enable-fast=all,O3 --prefix=/usr \
           --with-device=ch4:ofi --with-libfabric=/usr \
    && make -j$(nproc) \
    && make install \
    && ldconfig \
    && cd .. \
    && rm -rf mpich-4.1.tar.gz mpich-4.1

# Install libxsmm
RUN git clone https://github.com/libxsmm/libxsmm.git \
    && cd libxsmm \
    && make -j4 STATIC=0 BLAS=0

ENV PYFR_XSMM_LIBRARY_PATH=/libxsmm/lib/libxsmm.so

# Set base directory for pyCUDA cache
ENV XDG_CACHE_HOME /tmp

# Install PyFR
WORKDIR /
RUN pip install --upgrade pip \
    && pip install pyfr==1.15.0
    
