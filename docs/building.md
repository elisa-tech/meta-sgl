# Building meta-sgl with kas

Here are simple instructions for getting started building the long-term support
release of Yocto (scarthgap).  Documentation for kas can be found at 
https://kas.readthedocs.io/en/latest/

## Installing kas

To create a Python virtual environment to install kas run these commands:

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install kas
```

## Clone the meta-sgl build branch
After you have sourced the environment where kas is installed you may get the
kas configuration by cloning meta-sgl:

```bash
git clone https://github.com/elisa-tech/meta-sgl
```

## Running kas
Create a new project directory wherever you want and set the KAS_WORK_DIR 
environment variable to point to it.  Then run kas with the configuration file
for Yocto scarthgap release and qemuriscv64.

```bash
mkdir $PROJECT_DIR
KAS_WORK_DIR=$PROJECT_DIR
kas build meta-sgl/kas/sgl-scarthgap-qemuriscv64.yml
```

This should complete successfully and produce an image you can run in QEMU.

```bash
build/tmp-glibc/deploy/images/qemuriscv64/core-image-minimal-qemuriscv64.rootfs.ext4
```
