FROM python:3.7

#
# This Dockerfile can be used for building a container image containing the
# toggl-dinero tool.  It can be used with tools such as Docker and Podman.
#

WORKDIR /src

COPY MANIFEST.in README.rst setup.py setup.cfg /src/
COPY toggl_dinero/ toggl_dinero/

RUN python setup.py install
