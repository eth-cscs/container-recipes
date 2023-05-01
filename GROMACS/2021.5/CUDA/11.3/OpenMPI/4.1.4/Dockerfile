FROM docker.io/nvidia/cuda:11.0.3-devel-ubuntu20.04

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
       apt-get install -y --no-install-recommends \
            wget \
            cmake \
            automake \
            autoconf \
            libtool \
            libpmi2-0-dev \
            strace \
            python3 \
            zlib1g-dev \
            libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://github.com/ofiwg/libfabric/archive/v1.15.1.tar.gz \
    && tar xf v1.15.1.tar.gz \
    && cd libfabric-1.15.1 \
    && ./autogen.sh \
    && ./configure --prefix=/usr --with-cuda=/usr/local/cuda \
    && make -j$(nproc) \
    && make install \
    && ldconfig \
    && cd .. \
    && rm -rf v1.15.1.tar.gz libfabric-1.15.1

# Install OpenMPI 4.1.4 using libfabric libraries
RUN wget -q https://download.open-mpi.org/release/open-mpi/v4.1/openmpi-4.1.4.tar.gz \
    && tar xf openmpi-4.1.4.tar.gz \
    && cd openmpi-4.1.4 \
    && ./configure --with-libfabric=/usr --prefix=/usr --with-cuda \
        --with-pmi=/usr/include/slurm --with-pmi-libdir=/usr/lib/x86_64-linux-gnu \
        CFLAGS="-I/usr/include/slurm -L/usr/local/cuda/targets/x86_64-linux/lib/stubs/ -lcuda" \
    && make -j$(nproc) \
    && make install \
    && ldconfig \
    && cd .. \
    && rm -rf openmpi-4.1.4.tar.gz openmpi-4.1.4

# Install GROMACS
RUN wget -q http://ftp.gromacs.org/pub/gromacs/gromacs-2021.5.tar.gz \
    && tar xf gromacs-2021.5.tar.gz \
    && cd gromacs-2021.5 \
    && mkdir build && cd build \
    && cmake -DCMAKE_BUILD_TYPE=Release  \
             -DGMX_BUILD_OWN_FFTW=ON -DREGRESSIONTEST_DOWNLOAD=ON \
             -DGMX_MPI=on -DGMX_SIMD=AVX2_256 \
             -DGMX_GPU=CUDA \
             .. \
    && make -j$(nproc) \
    && make install \
    && cd ../.. \
    && rm -r gromacs-2021.5 gromacs-2021.5.tar.gz

ENV PATH=/usr/local/gromacs/bin:$PATH
ENV LD_LIBRARY_PATH=/usr/local/gromacs/lib:$LD_LIBRARY_PATH
ENV PKG_CONFIG_PATH=/usr/local/gromacs/lib/pkgconfig:$PKG_CONFIG_PATH
ENV MANPATH=/usr/local/gromacs/share/man/:$MANPATH
