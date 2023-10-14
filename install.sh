#!/bin/bash

udevrules=99-camera.rules
service=rpi-eclipse.service
daemon=eclipse.py

echo "copying udev rules.."
cp ${udevrules} /etc/udev/rules.d/
echo "copying ${daemon}.."
cp ${daemon} /usr/local/bin/
echo "copying ${service} unit.."
cp ${service} /etc/systemd/system/

echo "enabling units and reloading configs.."
systemctl daemon-reload
systemctl enable ${service}
udevadm control --reload-rules

echo "chmod scripts.."
chmod 755 /usr/local/bin/${daemon}
