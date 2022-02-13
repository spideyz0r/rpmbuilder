#!/bin/bash
mkdir -p /project/files/$2
cp -v /var/lib/mock/$1/result/* /project/files/$2
