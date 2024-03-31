# https://raw.githubusercontent.com/remote-android/redroid-doc/master/android-builder-docker/Dockerfile

FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
    && echo "install package for building AOSP" \
    && apt-get install -y git-core gnupg flex bison build-essential zip curl zlib1g-dev \
        gcc-multilib g++-multilib libc6-dev-i386 libncurses5 lib32ncurses5-dev x11proto-core-dev \
        libx11-dev lib32z1-dev libgl1-mesa-dev libxml2-utils xsltproc unzip fontconfig \
    && echo "install utils" \
    && apt-get install -y sudo rsync \
    && echo "install packages for build mesa3d or meson related" \
    && apt-get install -y python3-pip pkg-config python3-dev ninja-build \
    && pip3 install mako meson \
    && echo "packages for legacy mesa3d (< 22.0.0)" \
    && apt-get install -y python2 python-mako python-is-python2 python-enum34 gettext

RUN apt-get install -y vim git git-lfs

RUN (useradd -m -u {{ DOCKER_PUID }} {{ REDROID_BUILD_USER }} || true) \
    && echo "{{ REDROID_BUILD_USER }} ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers \
    && echo {{ REDROID_BUILD_USER }} >/root/username \
    && echo "{{ REDROID_BUILD_USER }}:{{ REDROID_BUILD_USER }}" | chpasswd && adduser {{ REDROID_BUILD_USER }} sudo


ENV HOME=/home/{{ REDROID_BUILD_USER }} \
    USER={{ REDROID_BUILD_USER }} \
    PATH=/src/.repo/repo:/usr/local/bin/scripts:/src/prebuilts/jdk/jdk8/linux-x86/bin/:$PATH

USER {{ DOCKER_PUID }}

CMD ["tail", "-f", "/dev/null"]