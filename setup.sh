# File: setup.sh
# Description: Full setup of the beaglebone software
# Author: Vilius Stonkus
# Created: 13/11/2022.

#!/bin/sh

# File should be in /home/debian directory

# Password
psw="temppwd"

# GitHub Repo Credentials
username=""
token=""

# Text color
Yellow='\033[0;33m'
NoColor='\033[0m'

if [ -z "${username}" ] || [ -z "${token}" ]; then
    printf "\n${Yellow}GitHub username: ${NoColor}"
    read username
    printf "${Yellow}GitHub personal API token: ${NoColor}"
    read token

    if [ -z "${username}" ] || [ -z "${token}" ]; then
        echo "${Yellow}GitHub username and/or API token are not specified${NoColor}"
        exit 1
    fi
fi

echo "${Yellow}Starting the setup...${NoColor}"

# Full clean of any existing files/directories except .sh file
echo "${Yellow}Deleting all files and directories...${NoColor}"
echo $psw | sudo -S find . ! -name 'setup.sh' -type d,f -exec rm -rf {} +

# Internet setup
echo "${Yellow}Setting up internet...${NoColor}"
echo $psw | sudo -S /sbin/route add default gw 192.168.7.1
echo $psw | sudo -S sh -c "echo 'domain localdomain\nsearch localdomain\nnameserver 8.8.8.8\nnameserver 8.8.4.4' > /etc/resolv.conf"
echo "${Yellow}Make sure the Beaglebone is connected to the internet using one of the methods below:\n
      - Network sharing from your device
      - Direct ethernet connection to a WiFi dongle 
     ${NoColor}"


printf "\n${Yellow}Is the internet connection established?(y/n)${NoColor}"
read internet
if [ "$internet" != "${internet#[Nn]}" ] || [ -z "${internet}" ]; then
    echo "${Yellow}Start the script when the internet connection is established${NoColor}"
    exit 1
fi

# Clone repository
echo "${Yellow}Cloning the repository...${NoColor}"
git clone -b master 'https://'$username':'$token'@github.com/UoBSat/PROVE-Pathfinder.git'

# Delete unnecessary files/directories
echo "${Yellow}Removing unnecessary files and directories...${NoColor}"
mv /home/debian/PROVE-Pathfinder/* /home/debian/
mv /home/debian/Flight-Software/* /home/debian/
echo $psw | sudo -S rm -rf PROVE-Pathfinder Flight-Software docs README.md LICENSE

# Install Python and its dependencies
echo "${Yellow}Installing Python dependencies...${NoColor}"
echo $psw | sudo -S apt update
echo $psw | sudo -S apt upgrade -y
echo $psw | sudo -S apt install wget software-properties-common build-essential libnss3-dev zlib1g-dev libgdbm-dev libncurses5-dev libssl-dev libffi-dev libreadline-dev libsqlite3-dev libbz2-dev -y
echo "${Yellow}Installing Python 3.8...${NoColor}"
wget https://www.python.org/ftp/python/3.8.2/Python-3.8.2.tgz
tar xvf Python-3.8.2.tgz
cd Python-3.8.2
./configure
echo $psw | sudo -S make altinstall
cd /home/debian
echo $psw | sudo -S rm -rf *.tgz
echo $psw | sudo -S rm -rf Python-3.8.2

# Install Python packages
echo "${Yellow}Installing Python packages...${NoColor}"
echo $psw | sudo -S pip3 install -r requirements.txt
echo $psw | sudo -S apt-get install libatlas-base-dev -y

# Install Basler library and dependencies
echo "${Yellow}Installing Basler library and dependencies...${NoColor}"
wget https://www.baslerweb.com/fp-1615275617/media/downloads/software/pylon_software/pylon_6.2.0.21487-deb0_armhf.deb
echo $psw | sudo -S apt install ./pylon_6.2.0.21487-deb0_armhf.deb
echo $psw | sudo -S apt install python-dev -y
echo $psw | sudo -S apt-get install swig -y
echo $psw | sudo -S apt-get install libopenjp2-7 -y
git clone https://github.com/basler/pypylon.git
cd pypylon
echo $psw | sudo -S pip3 install .
cd /home/debian
echo $psw | sudo -S rm -rf ./pylon_6.2.0.21487-deb0_armhf.deb
echo $psw | sudo -S rm -rf pypylon

# Install Tau 2 library and dependencies
echo "${Yellow}Installing Tau 2 library and dependencies...${NoColor}"
echo $psw | sudo -S apt install build-essential -y
echo $psw | sudo -S apt install cmake -y
cd /home/debian/Tasks/tau2/lib/libthermalgrabber 
cmake CMakeLists.txt
make
cd /home/debian/Tasks/tau2
g++ -std=c++11 /home/debian/Tasks/tau2/c++/src/capture.cpp -o main -I/home/debian/Tasks/tau2/lib/libthermalgrabber/inc -L/home/debian/Tasks/tau2/lib/libthermalgrabber/lib -lthermalgrabber
cd /home/debian/tests/tau_files
g++ -std=c++11 /home/debian/tests/tau_files/test_tau.cpp -o test_tau -I/home/debian/Tasks/tau2/lib/libthermalgrabber/inc -L/home/debian/Tasks/tau2/lib/libthermalgrabber/lib -lthermalgrabber
echo $psw | sudo -S find /home/debian/Tasks/tau2/lib/libthermalgrabber -mindepth 1 ! -regex '^/home/debian/Tasks/tau2/lib/libthermalgrabber/lib\(/.*\)?' -delete

# SD storage directory setup
echo "${Yellow}Setting up a directory for SD storage...${NoColor}"
cd /media && echo $psw | sudo -S mkdir -p SD1

# Scheduler service setup
echo "${Yellow}Setting up a scheduler service...${NoColor}"
echo $psw | sudo -S mv /home/debian/service-files/scheduler.sh /usr/bin/scheduler.sh
echo $psw | sudo -S mv /home/debian/service-files/scheduler.service /lib/systemd/scheduler.service
echo $psw | sudo -S ln -s /lib/systemd/scheduler.service /etc/systemd/system/scheduler.service
echo $psw | sudo -S systemctl daemon-reload
echo $psw | sudo -S systemctl enable scheduler.service
echo $psw | sudo -S systemctl start scheduler.service
echo $psw | sudo -S chmod u+x /usr/bin/scheduler.sh

# Telemetry service setup
echo "${Yellow}Setting up a telemetry service...${NoColor}"
echo $psw | sudo -S mv /home/debian/service-files/telemetry.sh /usr/bin/telemetry.sh
echo $psw | sudo -S mv /home/debian/service-files/telemetry.service /lib/systemd/telemetry.service
echo $psw | sudo -S ln -s /lib/systemd/telemetry.service /etc/systemd/system/telemetry.service
echo $psw | sudo -S systemctl daemon-reload
echo $psw | sudo -S systemctl enable telemetry.service
echo $psw | sudo -S systemctl start telemetry.service
echo $psw | sudo -S chmod u+x /usr/bin/telemetry.sh

# SDmount service setup
echo "${Yellow}Setting up a telemetry service...${NoColor}"
echo $psw | sudo -S mv /home/debian/service-files/SDmount.sh /usr/bin/SDmount.sh
echo $psw | sudo -S mv /home/debian/service-files/SDmount.service /lib/systemd/SDmount.service
echo $psw | sudo -S ln -s /lib/systemd/SDmount.service /etc/systemd/system/SDmount.service
echo $psw | sudo -S systemctl daemon-reload
echo $psw | sudo -S systemctl enable SDmount.service
echo $psw | sudo -S systemctl start SDmount.service
echo $psw | sudo -S chmod u+x /usr/bin/SDmount.sh

# Remove service files
echo "${Yellow}Removing unnecessary service files...${NoColor}"
cd /home/debian
echo $psw | sudo -S rm -rf service-files

echo "${Yellow}Setup Complete!${NoColor}"
echo "${Yellow}---------------${NoColor}"
echo "${Yellow}Rebooting...${NoColor}"

# Edit uEnv.txt to setup UART ports
echo "${Yellow}Enabbling UARTS and setting UART1 as primary serial console...${NoColor}"
echo $psw | sudo -S sh -c "echo 'uname_r=4.19.94-ti-r42\ndisable_uboot_overlay_video=1\ndisable_uboot_overlay_audio=1\nenable_uboot_overlays=1\nuboot_overlay_addr0=/lib/firmware/BB-UART1-00A0.dtbo\nuboot_overlay_addr1=/lib/firmware/BB-UART2-00A0.dtbo\nuboot_overlay_addr2=/lib/firmware/BB-UART4-00A0.dtbo\nuboot_overlay_addr3=/lib/firmware/BB-UART5-00A0.dtbo\nuboot_overlay_addr4=/lib/firmware/BB-UART3-00A0.dtbo\nuboot_overlay_pru=/lib/firmware/AM335X-PRU-RPROC-4-19-TI-00A0.dtbo\nenable_uboot_cape_universal=1\ncmdline=coherent_pool=1M net.ifnames=0 lpj=1990656 rng_core.default_quality=100 quiet\ncape_enable=capemgr.enable_partno=BB-UART1,BB-UART2,BB-UART4,BB-UART5\noptargs= console=ttyS1,115200' > /etc/resolv.conf"
echo $psw | sudo -S reboot