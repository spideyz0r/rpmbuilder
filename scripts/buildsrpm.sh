#!/bin/bash
echo "Recreating rpmbuild directory"
rm -rvf /root/rpmbuild/
rpmdev-setuptree
echo "Copying over sources"
cp -rpv /project/packages/${1}/SOURCES/* /root/rpmbuild/SOURCES
echo "Building SRPM"
rpmbuild --undefine=_disable_source_fetch -bs /project/packages/${1}/${1}.spec
