FROM freesurfer/freesurfer:7.2.0

RUN sed -i 's|mirrorlist=|#mirrorlist=|g' /etc/yum.repos.d/CentOS-* && \
    sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*


# Install extra packages
RUN yum -y update && \
    yum -y install epel-release && \
    yum -y install \
        git \
        curl \
        vim \
        gcc-c++ \
        python3 \
        python3-pip \
        eigen3-devel \
        zlib-devel \
        fftw-devel \
        qt5-qtbase-devel \
        mesa-libGL-devel \
        libpng-devel \
        make \
    && yum clean all

RUN echo "forcex"

COPY CentOS-SCLo-scl-rh.repo /etc/yum.repos.d/CentOS-SCLo-scl-rh.repo 

# Point repos to CentOS Vault (EOL archive)
RUN sed -i 's|mirrorlist=|#mirrorlist=|g' /etc/yum.repos.d/CentOS-* && \
    sed -i 's|#baseurl=http://mirror.centos.org/centos|baseurl=http://vault.centos.org/centos|g' /etc/yum.repos.d/CentOS-*

#RUN sed -i 's|' /etc/yum.repos.d/CentOS-SCLo-scl-rh.repo
#baseurl=https://vault.centos.org/7.9.2009/sclo/x86_64/sclo/

RUN yum -y install centos-release-scl

COPY CentOS-SCLo-scl.repo /etc/yum.repos.d/CentOS-SCLo-scl.repo

COPY CentOS-SCLo-scl-rh.repo /etc/yum.repos.d/CentOS-SCLo-scl-rh.repo

RUN yum -y install devtoolset-7-gcc
RUN yum -y install devtoolset-7-gcc-c++

#RUN yum -y install centos-release-scl && \
#    yum -y install devtoolset-9 && \
#    yum clean all

# Enable devtoolset-9 for all future commands
# SHELL ["/usr/bin/scl", "enable", "devtoolset-9", "bash", "-c"]

ENV PATH=/opt/rh/devtoolset-7/root/usr/bin:$PATH

RUN yum install -y qt5-qtbase-devel
RUN yum install -y qt5-qtsvg-devel


ENV PATH=/usr/lib64/qt5/bin:$PATH

# Clone and build MRtrix3
RUN git clone --branch 3.0.4 https://github.com/MRtrix3/mrtrix3.git /opt/mrtrix3 \
    && cd /opt/mrtrix3 \
    && ./configure \
    && ./build

# Add to PATH
ENV PATH="/opt/mrtrix3/bin:${PATH}"


##### MRTRIX HAS PROPERLY INSTALLED, DO NOT EDIT BEFORE THIS LINE 

#Python 3.10.6 (required for scilpy)
#WORKDIR /PYTHON3
#COPY Python-3.10.6.tgz /PYTHON3/
#RUN tar -xvf Python-3.10.6.tgz
#WORKDIR /PYTHON3/Python-3.10.6
#RUN ./configure --enable-optimizations
#RUN make
#RUN make install
#RUN yum install -y python3-pip
#RUN yum install -y openssl openssl-devel

###### PYTHON3.10.6 PROPERLY INSTALLED, DO NOT EDIT BEFORE THIS LINE

#Scilpy
RUN yum install -y blas blas-devel lapack lapack-devel
RUN yum -y install bzip2 bzip2-devel zlib-devel xz-devel libffi-devel wget 
RUN yum install -y sqlite-devel readline-devel libnsl tk-devel xz-devel

#openssl version is too low for python3.10 --> need at lest 1.1.1+ ?
RUN yum install -y openssl11-devel openssl11
WORKDIR /usr/local/openssl11/bin
RUN ln -s /usr/include/openssl11 /usr/local/openssl11/include
RUN ln -s /usr/lib64/openssl11 /usr/local/openssl11/lib64
RUN ln -s /usr/bin/openssl11 /usr/local/openssl11/bin/openssl


RUN yum -y install python3-devel python3-pip
#
##Python 3.10.6 (required for scilpy)
#https://stackoverflow.com/questions/60536472/building-python-and-openssl-from-source-but-ssl-module-fails
WORKDIR /PYTHON3
COPY Python-3.10.6.tgz /PYTHON3/
RUN tar -xvf Python-3.10.6.tgz
WORKDIR /PYTHON3/Python-3.10.6
#RUN ./configure --enable-optimizations --with-openssl=/usr/local/openssl11 --with-openssl-rpath=/usr/local/openssl11/lib64
RUN echo "flag"
RUN echo '#include <openssl/ssl.h>' > test.c && \
    gcc -I/usr/include/openssl11 -c test.c && \
    rm test.c test.o

# Make a structure Python expects
RUN mkdir -p /opt/openssl/include /opt/openssl/lib && \
    cp -r /usr/include/openssl11/* /opt/openssl/include/ && \
    cp -L /usr/lib64/openssl11/* /opt/openssl/lib/
RUN CPPFLAGS="-I/opt/openssl/include" \
    LDFLAGS="-L/opt/openssl/lib" \
    ./configure --enable-optimizations \
                --with-openssl=/opt/openssl \
                --with-openssl-rpath=/opt/openssl/lib

#RUN CPPFLAGS="-I/usr/include/openssl11" \
#    LDFLAGS="-L/usr/lib64/openssl11" \
#    ./configure --enable-optimizations --with-openssl=/usr --with-openssl-rpath=/usr/lib64/openssl11
RUN make
RUN make altinstall
RUN python3.10 -m ensurepip --upgrade
RUN python3.10 -m pip install --upgrade pip setuptools wheel
#RUN yum install -y python3-pip
#RUN yum install -y openssl openssl-devel
RUN git clone --branch 1.5.0 --single-branch https://github.com/scilus/scilpy.git /SCILPY
WORKDIR /SCILPY

RUN yum install -y gcc gcc-c++ python3-devel \
    blas-devel lapack-devel fftw-devel
RUN python3.10 -m pip install --upgrade pip setuptools wheel "numpy==1.23.5"
#RUN python3.10 -m pip install "Cython>=0.29,<0.30,!=0.29.29"
RUN python3.10 -m pip install "Cython==0.29.33"

RUN yum groupinstall -y "Development Tools"
RUN yum install -y \
        bzip2 bzip2-devel \
        zlib-devel \
        xz-devel \
        libffi-devel \
        wget \
        readline-devel \
        openssl-devel \
        bzip2 bzip2-devel \
        sqlite-devel \
        gcc gcc-c++ \
        gcc-gfortran \
        make \
        cmake \
        blas-devel \
        lapack-devel \
        fftw-devel \
        libtool \
        patch

RUN yum install -y python3-devel blas-devel lapack-devel fftw-devel
RUN yum install -y gcc-gfortran make cmake
RUN yum install -y openblas-devel lapack-devel
RUN git clone https://github.com/getspams/spams-python /SPAMS
WORKDIR /SPAMS
RUN python3.10 -m pip install -e .
WORKDIR /SCILPY
RUN python3.10 -m pip install .

######## SCILPY PROPERLY INSTALLED, DO NOT EDIT BEFORE THIS LINE

#tractseg
## need to install python 3.7.9
WORKDIR /PYTHON3.7
COPY Python-3.7.9.tgz /PYTHON3.7/
RUN tar -xvf Python-3.7.9.tgz
WORKDIR /PYTHON3.7/Python-3.7.9
#RUN ./configure --enable-optimizations --with-openssl=/usr/local/openssl11 --with-openssl-rpath=/usr/local/openssl11/lib64
RUN echo "flag"
RUN echo '#include <openssl/ssl.h>' > test.c && \
    gcc -I/usr/include/openssl11 -c test.c && \
    rm test.c test.o

# Make a structure Python expects
RUN CPPFLAGS="-I/opt/openssl/include" \
    LDFLAGS="-L/opt/openssl/lib" \
    ./configure --enable-optimizations \
                --with-openssl=/opt/openssl \
                --with-openssl-rpath=/opt/openssl/lib

#RUN CPPFLAGS="-I/usr/include/openssl11" \
#    LDFLAGS="-L/usr/lib64/openssl11" \
#    ./configure --enable-optimizations --with-openssl=/usr --with-openssl-rpath=/usr/lib64/openssl11
RUN make
RUN make altinstall
RUN python3.7 -m ensurepip --upgrade
RUN python3.7 -m pip install --upgrade pip setuptools wheel

RUN python3.7 -m pip install torch==1.6.0
RUN python3.7 -m pip install scikit-learn "matplotlib==3.5.3"
ENV SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL=True
RUN python3.7 -m pip install TractSeg==2.8.0

##### TRACTSEG HAS FINISHED INSTALLING

## Make sure to also install the weights for TRACTSEG
WORKDIR /WEIGHTS/.tractseg
COPY WEIGHTS/.tractseg /WEIGHTS/.tractseg/

#`now installing ants`
WORKDIR /APPS/INSTALLERS
RUN wget https://github.com/Kitware/CMake/releases/download/v3.23.0-rc2/cmake-3.23.0-rc2.tar.gz
RUN tar -xf cmake-3.23.0-rc2.tar.gz
WORKDIR cmake-3.23.0-rc2/
RUN ./bootstrap
RUN make
RUN make install
WORKDIR /APPS
RUN git clone https://github.com/ANTsX/ANTs.git
RUN scl enable devtoolset-7 bash

WORKDIR /APPS/ants_build
RUN source /opt/rh/devtoolset-7/enable \
 && cmake ../ANTs \
    -DCMAKE_INSTALL_PREFIX=/opt/ANTs \
    -DBUILD_SHARED_LIBS=ON \
    -DUSE_VTK=OFF \
    -DUSE_SYSTEM_ITK=OFF \
    -DBUILD_EXAMPLES=OFF \
 && make -j2

WORKDIR /APPS/ants_build/ANTS-build
RUN source /opt/rh/devtoolset-7/enable && make install

ENV PATH="/opt/ANTs/bin:${PATH}"

###### ANTS HAS FINISHED INSTALLING, DO NOT CHANGE LINES BEFORE THIS

#fsl
WORKDIR /APPS/INSTALLERS/FSL
RUN yum -y update && yum install -y \
    bc \
    libgomp \
    which \
    && yum clean all
RUN yum install -y file bc mesa-demos pulseaudio libquadmath gtk2 firefox libgomp
RUN wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fslconda/releases/fslinstaller.py && \
    python3.10 ./fslinstaller.py -d /APPS/FSL
#RUN wget -qO- https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py | \
#    python3.10 - -d /APPS/FSL -V 6.0.7.12

ENV FSLDIR=/APPS/FSL
ENV PATH=$PATH:$FSLDIR/bin
ENV FSLOUTPUTTYPE=NIFTI_GZ

ENV FSLOUTPUTTYPE=NIFTI_GZ
ENV FSLMULTIFILEQUIT=TRUE
ENV FSLTCLSH="${FSLDIR}/bin/fsltclsh"
ENV FSLWISH="${FSLDIR}/bin/fslwish"
ENV FSL_LOAD_NIFTI_EXTENSIONS=0
ENV FSL_SKIP_GLOBAL=0

######## FSL HAS FINISHED INSTALLING

WORKDIR /INPUTS
WORKDIR /OUTPUTS
RUN mv /WEIGHTS/.tractseg /root/

RUN rm /usr/bin/python3
RUN ln -s /usr/local/bin/python3.7 /usr/bin/python3

## Install c3d
RUN wget -O /APPS/INSTALLERS/c3d-1.0.0-Linux-x86_64.tar.gz "https://downloads.sourceforge.net/project/c3d/c3d/1.0.0/c3d-1.0.0-Linux-x86_64.tar.gz?r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fc3d%2Ffiles%2Fc3d%2F1.0.0%2Fc3d-1.0.0-Linux-x86_64.tar.gz%2Fdownload&ts=1571934949"
RUN tar -xf /APPS/INSTALLERS/c3d-1.0.0-Linux-x86_64.tar.gz -C /APPS/
ENV PATH=$PATH:/APPS/c3d-1.0.0-Linux-x86_64/bin
ENV LD_LIBRARY_PATH=/opt/ANTs/lib64/

## Copy the scripts into the Docker
WORKDIR /SCRIPTS
#COPY scripts/{aggregate_measurements.py,calc_scalars.sh,extract_singleshell.py,extract_singleshell.sh,get_bundle_measurements.sh,\
#            get_fs_global_wm_metrics.py,run_freesurfer.sh,run_proc.sh,run_t1_b0_reg.sh,run_tractseg.sh} /SCRIPTS
COPY scripts/*.py scripts/*.sh /SCRIPTS
RUN chmod +x /SCRIPTS/*.sh
RUN chmod +x /SCRIPTS/*.py
COPY Dockerfile /

## Run the processing command
ENTRYPOINT ["/SCRIPTS/run_proc.sh"]

#docker tag test kimm58/wm_lifespan_processing:v0.1

## pipeline

# DTI (extraction of lower shells, with option for thresholds)
# TractSeg
# Freesurfer (not sure about infant fs; may need to release that separately)
	# have a note that says: "InfantFS may be requested from XXX"
# Freesurfer WM Mask
# Aggregation of measurements into a CSV file


#now to do the actual scripts




#RUN source /APPS/FSL/etc/fslconf/fsl.sh

#RUN echo "source $FSLDIR/etc/fslconf/fsl.sh" >> /etc/.bashrc

#RUN make altinstall
#RUN make 2>&1 | tee build.log

#WORKDIR /APPS/ants_build/ANTS-build
#RUN make install 2>&1 | tee install.log
#ENV PATH="/opt/ANTs/bin:${PATH}"

#yum install centos-release-scl
#yum install devtoolset-7-gcc devtoolset-7-gcc-c++
#mkdir install build
#cd build
#ccmake ../ANTs
#`This was not wokring so I made the changes above (see newest change)`
#yum clean all
#yum install -y scl-utils
#yum install -y --nogpgcheck devtoolset-7 
#scl enable devtoolset-7 bash
#cd ants_build
#ccmake ../ANTs
#make 2>&1 | tee build.log
#cd ANTS-build
#make install 2>&1 | tee install.log
#echo 'export PATH="/opt/ANTs/bin/:$PATH"'

