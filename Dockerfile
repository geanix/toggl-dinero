FROM python:3.7

WORKDIR /src

COPY MANIFEST.in README.rst setup.py setup.cfg /src/
COPY toggldinero/ toggldinero/

RUN python setup.py install
