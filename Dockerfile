FROM ubuntu:trusty

MAINTAINER Arjan Verkerk <arjan.verkerk@nelen-schuurmans.nl>

# change the date to force rebuilding the whole image
ENV REFRESHED_AT 1972-12-25

# system dependencies
RUN apt update \
    && apt dist-upgrade --assume-yes \
    && apt install --assume-yes \
        python-pip \
        python-scipy \
    && apt-get clean --assume-yes \
    && pip install setuptools --upgrade \
    && pip install zc.buildout --upgrade

WORKDIR /code
