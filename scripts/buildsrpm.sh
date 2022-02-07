#!/bin/bash
rpmdev-setuptree
cp -rpv /project/SOURCES/* /root/rpmbuild/SOURCES
rpmbuild --undefine=_disable_source_fetch -bs /project/$1
