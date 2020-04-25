#!/bin/bash

#python and neo trellis lib, vlc lib for audio playback
echo "install libs and software for nightstand"
sudo apt-get install -y python3 python3-pip vlc
sudo pip3 install adafruit-circuitpython-neotrellis systemd python-vlc

echo "install bluetooth stuff"
sudo apt-get install -y libasound2-dev dh-autoreconf libortp-dev bluez pi-bluetooth bluez-tools libbluetooth-dev libusb-dev libglib2.0-dev libudev-dev libical-dev libreadline-dev libsbc1 libsbc-dev build-essential python3-dev libdbus-glib-1-dev libgirepository1.0-dev
