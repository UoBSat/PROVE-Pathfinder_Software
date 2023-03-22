# ArduCAM OV5642
This document provides instructions on a setup of ArduCAM ([product link](https://www.arducam.com/product/arducam-5mp-plus-spi-cam-arduino-ov5642/)), SPI interfacing on the beaglebone black, and image capturing.

For any questions, please contact *Vilius Stonkus* ([email](mailto:zh19737@bristol.ac.uk)).
## Prerequisites
1. ArduCAM official library from [here](https://github.com/ArduCAM/BeagleboneBlack). We are using modified version of the library which is tailored for our needs.
2. For compilation and Python bindings, ```cmake```, ```make``` and ```Cython``` packages are required
## Camera Connection
We are using the **SPI0 device**. On Debian 10.3, the pins described below connect to the **spidev0.0** channel.

Connect the ArduCAM to the following SPI pins:
- P9_22 => SPI0_SCLK
- P9_18 => SPI0_MOSI
- P9_21 => SPI0_MISO
- P9_17 => SPI0_CSO

The camera is also using the i2c interfacing for sensor communications. On Debian 10.3, the **i2c-2** device is used.

Connect the ArduCAM to the following I2C pins:
- P9_19 => I2C2_SCL
- P9_20 => I2C2_SDA

The camera can operate at either 3.3V or 5V.
## Enable SPI
By default, the SPI interface is disabled on the BeagleBone Black. Both SPI devices (0 and 1) have to be enabled manually. We are only using the SPI0 device for camera, so we will only enable this device.

The standard procedure is as follows (based on [this](https://www.element14.com/community/community/designcenter/single-board-computers/next-genbeaglebone/blog/2019/07/28/beaglebone-enable-spi-with-overlay)):
- Open the uEnv.txt file: ```sudo nano /boot/uEnv.txt```
- Scroll down to ```uboot_overlay_addr4```, uncomment it (or add a new entry) and include the SPI0 overlay file path: ```uboot_overlay_addr4=/lib/firmware/BB-SPIDEV0-00A0.dtbo```
- Reboot your Beaglebone: ```sudo reboot now```

The SPI0 interface should now be working. In order to test it, a spidev-test repository can be used ([repo](https://github.com/derekmolloy/exploringBB/tree/version2/chp08/spi/spidev_test)):
- Compile the spidev_test.c file: ```gcc spidev_test.c -o spidev_test```
- Run the spidev_test executable: ```./spidev_test```, or for a specific device: ``` ./spidev_test --device /dev/spidev0.0```

## Library Compilation
A custom Makefile has been created for the library compilation. It should be located at ```/home/debian/Tasks/arducam``` together with all other ArduCAM files.

To compile the library, simply run ```make``` in the same directory where the Makefile is located.

A shared object file ```pyBBBCAM.so``` will be generated, which will act as an importable Python module.

## Image Capture
To start the capturing process, simply run the ```arducam.py``` file from ```/home/debian/Tasks/arducam```.

The number of images to be captured is described by a list of timestamps.

This is the standard cmd to start the capturing: ```sudo python3 arducam.py --times [timestamps]```, where ```[timestamps]``` is a list of unix timestamps separated by single spacings.

E.g. ```sudo python3 arducam.py --times 1627652497 1627652597``` will capture 2 images at 2 specific timestamps.

## File Structure
The standard file structure of ```/home/debian/arducam/```.
```
├── arducam.py
├── default_properties.json
├── libs
│   ├── arducam-bbb
│   │   ├── arducam-bbb      // Library header files
│   │   │   ├── BBBCAM.h
│   │   │   ├── BBBCAM_OV5642_DigitalCamera.h
│   │   │   ├── memorysaver.h
│   │   │   ├── mt9d111_regs.h
│   │   │   ├── ov2640_regs.h
│   │   │   ├── ov3640_regs.h
│   │   │   ├── ov5642_regs.h
│   │   │   ├── ov7660_regs.h
│   │   │   ├── ov7670_regs.h
│   │   │   ├── ov7675_regs.h
│   │   │   ├── ov7725_regs.h
│   │   │   └── UTFT_SPI.h
│   │   ├── build            // Library build files generated with cmake
│   │   │   ├── CMakeCache.txt
│   │   │   ├── CMakeFiles
│   │   │   │   ├── 3.13.4
│   │   │   │   │   ├── CMakeCCompiler.cmake
│   │   │   │   │   ├── CMakeCXXCompiler.cmake
│   │   │   │   │   ├── CMakeDetermineCompilerABI_C.bin
│   │   │   │   │   ├── CMakeDetermineCompilerABI_CXX.bin
│   │   │   │   │   ├── CMakeSystem.cmake
│   │   │   │   │   ├── CompilerIdC
│   │   │   │   │   │   ├── a.out
│   │   │   │   │   │   ├── CMakeCCompilerId.c
│   │   │   │   │   │   └── tmp
│   │   │   │   │   └── CompilerIdCXX
│   │   │   │   │       ├── a.out
│   │   │   │   │       ├── CMakeCXXCompilerId.cpp
│   │   │   │   │       └── tmp
│   │   │   │   ├── arducam-bbb.dir
│   │   │   │   │   ├── build.make
│   │   │   │   │   ├── C.includecache
│   │   │   │   │   ├── cmake_clean.cmake
│   │   │   │   │   ├── cmake_clean_target.cmake
│   │   │   │   │   ├── DependInfo.cmake
│   │   │   │   │   ├── depend.internal
│   │   │   │   │   ├── depend.make
│   │   │   │   │   ├── flags.make
│   │   │   │   │   ├── link.txt
│   │   │   │   │   ├── progress.make
│   │   │   │   │   └── source
│   │   │   │   │       ├── BBBCAM.c.o
│   │   │   │   │       ├── BBBCAM_OV5642_DigitalCamera.c.o
│   │   │   │   │       └── UTFT_SPI.c.o
│   │   │   │   ├── cmake.check_cache
│   │   │   │   ├── CMakeDirectoryInformation.cmake
│   │   │   │   ├── CMakeOutput.log
│   │   │   │   ├── CMakeTmp
│   │   │   │   ├── feature_tests.bin
│   │   │   │   ├── feature_tests.c
│   │   │   │   ├── feature_tests.cxx
│   │   │   │   ├── Makefile2
│   │   │   │   ├── Makefile.cmake
│   │   │   │   ├── progress.marks
│   │   │   │   └── TargetDirectories.txt
│   │   │   ├── cmake_install.cmake
│   │   │   ├── libarducam-bbb.a
│   │   │   └── Makefile
│   │   ├── CMakeLists.txt
│   │   └── source           // Library source files
│   │       ├── BBBCAM.c
│   │       ├── BBBCAM_OV2640_DigitalCamera.c
│   │       ├── BBBCAM_OV2640_Playback.c
│   │       ├── BBBCAM_OV3640_Playback.c
│   │       ├── BBBCAM_OV5642_DigitalCamera.c
│   │       ├── BBBCAM_OV5642_Playback.c
│   │       ├── BBBCAM_OV7670_Playback.c
│   │       ├── DefaultFonts_SPI.c
│   │       └── UTFT_SPI.c
│   └── system_memory.c      // CPU and RAM consumption
├── Makefile                 // Custom Makefile for library compilation
├── notes
│   └── configuration properties.txt
├── pyBBBCAM.pyc
├── pyBBBCAM.pyx             // Python bindings for C functions, using Cython wrapper
├── pyBBBCAM.so              // Shared object file. Acts as a Python module
├── README.md
├── setup.py                 // Setup file for Cython wrapper
└── spi_test                 // SPI testing using Python and C
    ├── spidev_test
    ├── spidev_test.c
    └── spitest.py
```