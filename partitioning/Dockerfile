# To avoid any problems regarding Python, C, make, etc. this image is used to mount a directory containing *.gml
# files, calculate the partitions using pymetis and then write them into the mounted directory.
# start image with:
# docker run --rm -v d:/partitioning:/tmp/partitioning pymetis_container
# or in interactive mode:
# docker run --rm -ti --entrypoint=/bin/bash -v d:/partitioning:/tmp/partitioning pymetis_container
FROM python:3.7-buster
RUN apt-get update && apt-get -y install cmake && apt-get -y install vim
RUN pip install pybind11 && pip install pymetis && pip install networkx && pip install numpy
WORKDIR /tmp
COPY datasets /tmp/datasets
COPY create_partitions.py .
CMD ["python", "./create_partitions.py"]