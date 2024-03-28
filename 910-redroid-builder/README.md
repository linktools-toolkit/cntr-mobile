# Build redroid with docker

```bash
export REDROID_BUILD_PATH=~/Project/redroid

#####################
# fetch code
#####################
mkdir $REDROID_BUILD_PATH && cd $REDROID_BUILD_PATH

repo init -u https://github.com/redroid-rockchip/platform_manifests.git -b redroid-12.0.0 --depth=1 --git-lfs
repo sync -c

# 修改build/soong/cc/config/global.go，向commonGlobalCflags数组添加全局cflags "-DANDROID_12"
vim build/soong/cc/config/global.go
# var (
#	// Flags used by lots of devices.  Putting them in package static variables
#	// will save bytes in build.ninja so they aren't repeated for every file
#	commonGlobalCflags = []string{
#		"-DANDROID_12",  <================================================ add this line
#		"-DANDROID",
#		"-fmessage-length=0",

#####################
# create builder
#####################
./manager.py add redroid-builder

#####################
# start builder
#####################
./manager.py up

#####################
# build redroid in container
#####################
./manager.py exec redroid-builder shell

cd /src

. build/envsetup.sh

lunch redroid_arm64-userdebug
export TARGET_BOARD_PLATFORM_GPU=mali-G52
export TARGET_RK_GRALLOC_VERSION=4

# start to build
m

#####################
# create redroid image in *HOST*
#####################
cd $REDROID_BUILD_PATH/out/target/product/redroid_arm64

sudo mount system.img system -o ro
sudo mount vendor.img vendor -o ro
sudo tar --xattrs -c vendor -C system --exclude="./vendor" . | DOCKER_DEFAULT_PLATFORM=linux/arm64 docker import -c 'ENTRYPOINT ["/init", "androidboot.hardware=redroid"]' - redroid
sudo umount system vendor
```

Run docker container with redroid image
```bash
sudo docker run -itd --name redroid --privileged -v ~/data:/data -v /dev/mali0:/dev/mali0 -p 5557:5555 redroid androidboot.redroid_gpu_mode=mali
```

## Misc

Export redroid image to other machine
```bash
docker save redroid | bzip2 | ssh root@10.10.10.30 docker load
```

Fix webview error: https://github.com/remote-android/redroid-doc/issues/464
```bash
## install lfs
# apt install git-lfs
## then run
repo forall -g lfs -c git lfs pull
```
