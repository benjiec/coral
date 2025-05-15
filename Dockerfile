FROM continuumio/miniconda3

RUN apt-get update
RUN apt-get install -y wget cmake g++ m4 xz-utils libgmp-dev unzip zlib1g-dev libboost-program-options-dev libboost-serialization-dev libboost-regex-dev libboost-iostreams-dev libtbb-dev libreadline-dev pkg-config git liblapack-dev libgsl-dev flex bison libcliquer-dev gfortran file dpkg-dev libopenblas-dev rpm

# build mmseqs2
RUN mkdir /mmseqs2
WORKDIR /mmseqs2
RUN git clone https://github.com/soedinglab/MMseqs2.git
WORKDIR /mmseqs2/MMseqs2/build
RUN cmake ..
RUN make
RUN make install

# install lovis4u
RUN python3 -m pip install lovis4u
RUN mkdir /lovis4u
WORKDIR /lovis4u
RUN lovis4u --data
RUN lovis4u -smp mmseqs
RUN lovis4u --get-hmms

# install diamond aligner
RUN mkdir /diamond
WORKDIR /diamond
RUN wget http://github.com/bbuchfink/diamond/releases/download/v2.1.11/diamond-linux64.tar.gz
RUN tar xzf diamond-linux64.tar.gz
RUN ln -sf /diamond/diamond /usr/local/bin/

# install SCIP solver
RUN conda install --c conda-forge pyscipopt

# install CarveMe
RUN pip install carveme

RUN mkdir /coral
WORKDIR /coral
