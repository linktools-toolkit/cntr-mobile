#!/bin/bash

. build/envsetup.sh || exit 1
lunch redroid_arm64-userdebug || exit 1

# start to build
m || exit 1
