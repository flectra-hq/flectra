#!/usr/bin/env bash

sudo mount -o remount,rw /
sudo git --work-tree=/home/pi/flectra/ --git-dir=/home/pi/flectra/.git pull
sudo mount -o remount,ro /
(sleep 5 && sudo reboot) &
