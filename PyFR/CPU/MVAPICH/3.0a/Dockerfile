FROM docker.io/ubuntu:22.04

LABEL com.pyfr.version="1.15.0"

# Install system dependencies
RUN apt-get update && apt-get install -y   \
        unzip                       \
        git                         \
        wget                        \
        build-essential             \
        bison                       \
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

# Install MVAPICH 3.0a
RUN wget -q http://mvapich.cse.ohio-state.edu/download/mvapich/mv2/mvapich2-3.0a.tar.gz \
    && tar xf mvapich2-3.0a.tar.gz \
    && cd mvapich2-3.0a \
    && ./configure --prefix=/usr --disable-fortran --enable-fast=all,O3 --with-libfabric=/usr \
       --with-device=ch4:ofi --disable-omb \
    && make -j$(nproc) \
    && make install \
    && ldconfig \
    && cd .. \
    && rm -rf mvapich2-3.0a.tar.gz mvapich2-3.0a

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
    
