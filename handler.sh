#!/bin/bash
set -e
packages=$(git diff main... --name-only | grep spec$ | cut -d / -f2)

function build()
{
	pkg=$1
	release=$(grep Release packages/$1/$1.spec | cut -d ":" -f2  | tr -d " " | cut -b -1)
	version=$(grep Version packages/$1/$1.spec | cut -d ":" -f2  | tr -d " ")
	name="${pkg}-${version}-${release}.fc34.src.rpm"
	echo "###################################################"
	echo "Building $pkg => $name. Logs in $name.log"
	time docker run -it -d --name ${pkg}-build -v /home/circleci/project:/project --cap-add=SYS_ADMIN --security-opt apparmor:unconfined mockzor &>$pkg.log
	echo "Building SRPM for $pkg"
	time docker exec ${pkg}-build /project/scripts/buildsrpm.sh $pkg &>>$pkg.log
	echo "Running mock for $name"
	time docker exec ${pkg}-build /project/scripts/runmock.sh rocky+epel-8-x86_64 $name &>>$pkg.log || echo "Build for $pkg has failed!"
	echo "Copying $pkg RPMs"
	time docker exec ${pkg}-build /project/scripts/copyrpms.sh rocky+epel-8-x86_64 $name 2>&1 | tee $pkg.log
}

for pkg in $packages
do
	build $pkg&
done
wait
echo "All RPMs were built with success!"