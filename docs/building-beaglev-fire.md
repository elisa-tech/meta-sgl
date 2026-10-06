# BeagleV-Fire - Building & Running

## Overview

This document describes the process of running Space Grade Linux (SGL) on the
BeagleV-Fire development board.
The BeagleV-Fire is powered by a Microchip PolarFire® MPFS025T 5x core RISC-V System on Chip (SoC) with FPGA fabric.

## Build SGL for the BeagleV

Follow the [meta-sgl building guide](building.html) with the `sgl-scarthgap` configuration and `beaglev-fire` machine target:

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install kas

git clone https://github.com/space-grade-linux/meta-sgl
export PROJECT_DIR=sgl-beaglev-fire
mkdir $PROJECT_DIR
KAS_WORK_DIR=$PROJECT_DIR kas build meta-sgl/kas/sgl-scarthgap-beaglev-fire.yml
```

This is the base configuration that combines Yocto `scarthgap`, the SGL distro (`meta-sgl-core`) and the Microchip BSP layers. More information can be found in the section about configuration in the [meta-sgl building guide](building.html#choosing-a-configuration) or in the [meta-sgl Github repository](https://github.com/space-grade-linux/meta-sgl/tree/main/kas).


This produces the image for the board under `$PROJECT_DIR/build/tmp-glibc/deploy/images/beaglev-fire/`:
- `core-image-minimal-beaglev-fire.rootfs-<TIMESTAMP>.wic.gz`, the compressed disk image for the eMMC
- `core-image-minimal-beaglev-fire.rootfs-<TIMESTAMP>.wic.bmap`, block map used by `bmaptool`

::: info
The first build downloads all sources and compiles the complete distribution, which can take several hours depending on the host system.
:::


## Connect the BeagleV-Fire

Two connections to the host computer:

- **Serial console** — connect the 3.3 V USB-to-serial adapter to the UART debug header of the BeagleV-Fire. The HSS, U-Boot and Linux all use this console.
- **USB-C** — powers the board and, during flashing, exposes the eMMC to the host as a USB mass-storage device.

Optionally, connect the Ethernet port to a network with a DHCP server.


## Flash the image to the eMMC

1. Power the board through USB-C while the serial console is open.
2. When the HSS prints its boot countdown, press any key to stop autoboot and enter the HSS prompt.
3. Expose the eMMC to the host as a USB mass-storage device:

   ```bash
   >> usbdmsc
   ```

::: info
Shortcut: Just hold down the USER button and reset the board.
This will also set the board into the USB mass-storage mode.
:::


4. On the host, identify the new block device:

   ```bash
   lsblk
   ```

5. Write the image with `bmaptool`, replacing `/dev/sdX` with the eMMC device:

   ::: danger
   The following command overwrites the entire target device. Verify the device name with `lsblk` before running it.
   :::

   ```bash
   cd $KAS_WORK_DIR/build/tmp-glibc/deploy/images/beaglev-fire
   sudo bmaptool copy core-image-minimal-beaglev-fire.rootfs.wic.gz /dev/sdX
   ```

6. Once `bmaptool` has finished, press `Ctrl-C` in the HSS console to end the mass-storage session, then reset or power-cycle the board.


## Boot Verification

After the reset, the HSS starts U-Boot, which loads the SGL kernel from the eMMC. Serial console output:

```bash
HSS: decompressing from eNVM to L2 Scratch ... Passed
DDR training ...
...

---------------------------------
--        BeagleV-Fire         --
---------------------------------

[5.529694] PolarFire(R) SoC Hart Software Services (HSS) - version 0.99.36-BVF-0.3.0
MPFS HAL version 2.2.104 / DDR Driver version 0.4.023 / Mi-V IHC version 0.1.1 / BOARD=bvf
(c) Copyright 2017-2022 Microchip FPGA Embedded Systems Solutions.

...
[...] Boot image set name: "PolarFire-SoC-HSS::U-Boot"

U-Boot 2023.07.02-linux4microchip+fpga-2025.07 (Jul 22 2025 - 09:10:12 +0000)

...
Starting kernel ...

[    0.000000] Linux version 6.12.22-linux4microchip+fpga-2025.07-g...
[    0.000000] Machine model: BeagleBoard BeagleV-Fire
...
Welcome to Space Grade Linux 0.1 (wone)!
...
Space Grade Linux 0.1 beaglev-fire ttyS0
beaglev-fire login:
```

::: info
The default login is `root` without a password.
:::

## Testing SGL

The following commands confirm that the system is running SGL on the board:

```bash
cat /etc/os-release
uname -a
systemctl --failed       # should list no failed units
```

When the Ethernet port is connected, SGL requests an address via DHCP (systemd-networkd, `wired.network` from `meta-sgl-core`):

```bash
networkctl status
ip addr show
```

## Further Reading

- [BeagleV-Fire documentation](https://docs.beagleboard.org/latest/boards/beaglev/fire/)
- [meta-mchp (Microchip Yocto BSP)](https://github.com/linux4microchip/meta-mchp)
