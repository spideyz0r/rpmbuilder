#!/bin/bash
set -e

function build()
{
	pkg=$1
	branch=$(echo $2 | cut -d ":" -f1)
	mock_env=$(echo $2 | cut -d ":" -f2)
	[[ -e packages/$pkg/repo ]] && repo=$(cat packages/$pkg/repo | tr -d " " | tr -d "\n")
	[[ -e packages/$pkg/repo ]] && [[ ! -d packages/$pkg/$pkg ]] && git clone --recursive $repo packages/$pkg/$pkg &>>${LOGS_DIR}/${pkg}.log
	[[ -e packages/$pkg/repo ]] && git --git-dir=packages/$pkg/$pkg/.git --work-tree=packages/$pkg/$pkg reset --hard origin/$branch &>>${LOGS_DIR}/${pkg}.log
	release=$(grep 'Release:' packages/$pkg/$pkg/$pkg.spec | cut -d ":" -f2  | tr -d " " | cut -b -1)
	version=$(grep 'Version:' packages/$pkg/$pkg/$pkg.spec | cut -d ":" -f2  | tr -d " ")
	name="${pkg}-${version}-${release}.fc34.src.rpm"
	echo "#########################################################################"
	echo "### Building $pkg => $name"
	echo "### Mockenv: $mock_env"
	echo "### Branch: $branch"
	echo "### Logs in $name.log"
	echo "#########################################################################"
	docker run -it -d --name ${pkg}-${branch}-build -v /home/circleci/project:/project --cap-add=SYS_ADMIN --security-opt apparmor:unconfined spideyz0r/mockzor &>>${LOGS_DIR}/${pkg}.log
	echo "### Building SRPM for $pkg"
	docker exec ${pkg}-${branch}-build /project/scripts/buildsrpm.sh $pkg &>>${LOGS_DIR}/${pkg}.log
	echo "### Running mock for $name"
	docker exec ${pkg}-${branch}-build /project/scripts/runmock.sh $mock_env $name &>>${LOGS_DIR}/${pkg}.log
	echo "### Copying $pkg RPMs"
	docker exec ${pkg}-${branch}-build /project/scripts/copyrpms.sh $mock_env $name &>>${LOGS_DIR}/${pkg}.log
}

LOGS_DIR=logs
mkdir -p $LOGS_DIR
# list only files Modified, Added, Copied, Renamed
packages=$(git diff main... --diff-filter=MACR --name-only | grep "packages/" | cut -d "/" -f2 | sort | uniq)

for pkg in $packages
do
	for env in $(cat packages/${pkg}/env)
	do
		build $pkg $env
	done
done
# wait
echo "All RPMs were built with success!"
ls -R /project/files