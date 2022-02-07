FROM fedora:34
RUN dnf -y --setopt=tsflags='' install dnf-data dnf-plugins-core dnf-utils libdnf dnfdragora vim mock rpm-build rpmdevtools
COPY ./mock-conf/rocky+epel-8-x86_64.cfg /etc/mock
COPY ./mock-conf/rocky-8.tpl /etc/mock/templates
