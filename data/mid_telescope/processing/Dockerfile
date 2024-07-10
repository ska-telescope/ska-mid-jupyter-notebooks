FROM ubuntu:20.04

    ENV DEBIAN_FRONTEND=noninteractive
    ENV threads=4
    ENV PYTHONPATH=/opt/meersoft/lib/python3.8/site-packages/
    ENV LD_LIBRARY_PATH=/opt/meersoft/lib:/usr/local/lib/
    ENV PATH=${PATH}:/opt/meersoft/bin
    ENV NUMBA_CACHE_DIR=/tmp/
    
    # Ubuntu apt installs
    RUN apt-get update \
    && apt-get --yes install --no-install-recommends \	
        ca-certificates \	
        gnupg \	
	    gpg-agent \	
        wget \	
        python-is-python3 \
        build-essential \
        gfortran \
        python3-pip \
        python3-dev \
        python3-setuptools \
        cmake \
        libncurses5-dev \
        libopenmpi-dev \
        libreadline-dev \
        libhdf5-serial-dev \
        flex \
        bison \
        libblas-dev \
        libcfitsio-dev \
        libfftw3-dev \
        libgsl-dev \
        liblapacke-dev \
        wcslib-dev \
        libboost-numpy-dev \
        git \
    && rm -rf /var/lib/apt/lists/*

    # Manually install boost
    RUN cd / \
    && wget https://boostorg.jfrog.io/artifactory/main/release/1.79.0/source/boost_1_79_0.tar.bz2 \
    && tar xvf boost_1_79_0.tar.bz2 \
    && cd boost_1_79_0 \
    && bash bootstrap.sh && ./b2 install \
    && cd / && rm -r boost_1_79_0 boost_1_79_0.tar.bz2
    
    # 
    RUN mkdir /opt/meersoft/
    
    RUN pip3 install -U pip
    RUN pip3 install -U numpy==1.20.3 astropy aplpy ipython pylint astroquery
    
    # Install pybdsf
    RUN pip3 install bdsf==1.10.2
    
    # Install casacore data
    RUN mkdir -p /opt/meersoft/data \
    && cd /opt/meersoft/data \
    && wget ftp://anonymous@ftp.astron.nl/outgoing/Measures/WSRT_Measures.ztar \
    && tar xvf WSRT_Measures.ztar \
    && rm WSRT_Measures.ztar
    
    # Build casacore
    RUN cd / & wget https://github.com/casacore/casacore/archive/v3.5.0.tar.gz \
    && tar xvf v3.5.0.tar.gz && cd casacore-3.5.0 \
    && mkdir build && cd build \
    && cmake \
        -DCMAKE_INSTALL_PREFIX=/opt/meersoft/ \
        -DDATA_DIR=/opt/meersoft/data \
        -DUSE_OPENMP=ON -DUSE_THREADS=OFF \
        -DUSE_HDF5=ON -DCMAKE_BUILD_TYPE=Release \
        -DBUILD_PYTHON=OFF \
        -DBUILD_PYTHON3=ON -DPYTHON3_LIBRARY=/usr/lib/x86_64-linux-gnu/libpython3.8m.so \
        -DPYTHON3_INCLUDE_DIR=/usr/include/python3.8m/ -DPYTHON3_EXECUTABLE=/usr/bin/python3 \
        -DCMAKE_CXX_FLAGS="-fsigned-char -O2 -DNDEBUG" ../ \
    && make -j $threads && make install && cd / && rm -rf v3.5.0.tar.gz casacore-3.5.0
    
    # Install python casacore
    RUN cd / & wget https://github.com/casacore/python-casacore/archive/v3.5.2.tar.gz \
    && tar xvf v3.5.2.tar.gz && cd python-casacore-3.5.2 \
    && mkdir -p /opt/meersoft/lib/python3.8/site-packages/ \
    && export PYTHONPATH=/opt/meersoft/lib/python3.8/site-packages/ \
    && export LD_LIBRARY_PATH=/opt/meersoft/lib \
    && export PATH=/opt/meersoft/include:${PATH} \
    && python3 ./setup.py build_ext -I/opt/meersoft/include -L/opt/meersoft/lib \
    && python3 ./setup.py install --prefix=/opt/meersoft/ \
    && cd / && rm -rf python-casacore-3.5.2 v3.5.2.tar.gz
    
    # Download NRAO CASA
    RUN pip3 install casatasks==6.5.3.28
    RUN pip3 install casadata
    
    # Install KATbeam
    RUN cd / && git clone https://github.com/ska-sa/katbeam.git \
    && cd katbeam && git checkout 5ce6fcc35471168f4c4b84605cf601d57ced8d9e \
    && export PYTHONPATH=/opt/meersoft/lib/python3.8/site-packages/ \
    && python3 ./setup.py install --prefix=/opt/meersoft \
    && cd / && rm -rf katbeam
    
    # Install Everybeam
    RUN cd / && git clone https://git.astron.nl/RD/EveryBeam.git \
    && cd EveryBeam && git checkout v0.4.0 \
    && mkdir build && cd build \
    && export PYTHONPATH=/opt/meersoft/lib/python3.8/site-packages/ \
    && cmake -DCMAKE_INSTALL_PREFIX=/opt/meersoft/ ../ \
    && make -j $threads && make install \
    && cd / && rm -rf EveryBeam

    # Install IDG
    RUN cd / && git clone https://gitlab.com/astron-idg/idg.git \
    && cd idg && git checkout 1.1.0 \
    && mkdir build && cd build \
    && cmake \
	-DCMAKE_INSTALL_PREFIX=/opt/meersoft/ \
	-DBUILD_LIB_CUDA=Off \
	../ \
    && make && make install && cd / && rm -rf idg
    
    # Install wsclean
    RUN cd / && git clone https://gitlab.com/aroffringa/wsclean.git \
    && cd wsclean && git checkout v3.2 \
    && mkdir build && cd build \
    && export PYTHONPATH=/opt/meersoft/lib/python3.8/site-packages/ \
    && cmake \
	-DCMAKE_PREFIX_PATH=/opt/meersoft/ \
        -DCASACORE_ROOT_DIR=/opt/meersoft/ \
	-DCMAKE_INSTALL_PREFIX=/opt/meersoft/ ../ \
    && make -j $threads && make install \
    && cd / && rm -rf wsclean
    
    # Install eidos beam
    RUN cd / \
    && git clone https://github.com/ratt-ru/eidos \
    && cd eidos \
    && export PYTHONPATH=/opt/meersoft/lib/python3.8/site-packages/ \
    && python3 setup.py install \
    && cd ../ && rm -rf eidos
    
    # Install tricolour
    RUN cd / \
    && git clone https://github.com/ska-sa/tricolour.git \
    && cd tricolour \
    && git checkout 0.1.8 \
    && export PYTHONPATH=/opt/meersoft/lib/python3.8/site-packages/ \
    && python3 setup.py install \
    && cd ../ && rm -rf tricolour
    
    # Add tricolour strategy file to 
    RUN mkdir /opt/meersoft/yaml
    COPY ./tricolour.yaml /opt/meersoft/yaml/tricolour.yaml
    COPY ./tricolour_oxkat.yaml /opt/meersoft/yaml/tricolour_oxkat.yaml
    RUN chmod 755 /opt/meersoft/yaml/tricolour.yaml
    RUN chmod 755 /opt/meersoft/yaml/tricolour_oxkat.yaml
    
    # Install breizorro
    RUN cd / \
    && git clone https://github.com/ratt-ru/breizorro.git \
    && cd breizorro \
    && git checkout 5e3ad86 \
    && export PYTHONPATH=/opt/meersoft/lib/python3.8/site-packages/ \
    && python3 setup.py install \
    && cd ../ && rm -rf breizorro