FROM docker.io/ubuntu:22.04

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
       apt-get install -y --no-install-recommends \
            build-essential \
            ca-certificates \
            wget \
            cmake \
            bison \
            automake \
            autoconf \
            libtool \
            libpmi2-0-dev \
            strace \
            python3 \
            zlib1g-dev \
            libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://github.com/ofiwg/libfabric/archive/v1.14.1.tar.gz \
    && tar xf v1.14.1.tar.gz \
    && cd libfabric-1.14.1 \
    && ./autogen.sh \
    && ./configure --prefix=/usr \
    && make -j$(nproc) \
    && make install \
    && ldconfig \
    && cd .. \
    && rm -rf v1.14.1.tar.gz libfabric-1.14.1

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

# Install GROMACS
RUN wget -q http://ftp.gromacs.org/pub/gromacs/gromacs-2021.5.tar.gz \
    && tar xf gromacs-2021.5.tar.gz \
    && cd gromacs-2021.5 \
    && mkdir build && cd build \
    && cmake -DCMAKE_BUILD_TYPE=Release  \
             -DGMX_BUILD_OWN_FFTW=ON \
             -DGMX_MPI=on -DGMX_SIMD=AVX2_256 \
             .. \
    && make -j$(nproc) \
    && make install \
    && cd ../.. \
    && rm -r gromacs-2021.5 gromacs-2021.5.tar.gz

ENV PATH=/usr/local/gromacs/bin:$PATH
ENV LD_LIBRARY_PATH=/usr/local/gromacs/lib:$LD_LIBRARY_PATH
ENV PKG_CONFIG_PATH=/usr/local/gromacs/lib/pkgconfig:$PKG_CONFIG_PATH
ENV MANPATH=/usr/local/gromacs/share/man/:$MANPATH
