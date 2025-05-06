FROM python:3

RUN apt-get update
RUN apt-get install -y vim
RUN apt-get install -y man
RUN apt-get install -y cmake

# build mmseqs2
RUN mkdir /mmseqs2
WORKDIR /mmseqs2
RUN git clone https://github.com/soedinglab/MMseqs2.git
WORKDIR /mmseqs2/MMseqs2/build
RUN cmake ..
RUN make
RUN make install

RUN python3 -m pip install lovis4u

RUN mkdir /coral
WORKDIR /coral
COPY . .
