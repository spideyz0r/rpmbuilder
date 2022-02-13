#!/bin/bash
set -e
packages=$(git diff main... --name-only | grep spec$ | cut -d / -f2)

function build()
{
	pkg=$1
	release=$(grep 'Release:' packages/$1/$1.spec | cut -d ":" -f2  | tr -d " " | cut -b -1)
	version=$(grep 'Version:' packages/$1/$1.spec | cut -d ":" -f2  | tr -d " ")
	name="${pkg}-${version}-${release}.fc34.src.rpm"
	echo "###################################################"
	echo "### Building $pkg => $name. Logs in $name.log"
	echo "###################################################"
	docker run -it -d --name ${pkg}-build -v /home/circleci/project:/project --cap-add=SYS_ADMIN --security-opt apparmor:unconfined mockzor
	echo "### Building SRPM for $pkg"
	docker exec ${pkg}-build /project/scripts/buildsrpm.sh $pkg
	echo "### Running mock for $name"
	docker exec ${pkg}-build /project/scripts/runmock.sh rocky+epel-8-x86_64 $name
	echo "### Copying $pkg RPMs"
	docker exec ${pkg}-build /project/scripts/copyrpms.sh rocky+epel-8-x86_64 $name
}

for pkg in $packages
do
	build $pkg
done
wait
echo "All RPMs were built with success!"