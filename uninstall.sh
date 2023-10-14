#!/bin/bash

udevrules=99-camera.rules
service=rpi-eclipse.service
daemon=eclipse.py

echo "delete udev rules.."
rm -f /etc/udev/rules.d/${udevrules}
echo "delete daemon script.."
rm -f /usr/local/bin/${daemon}
echo "disable systemd units.."
systemctl disable ${service}
echo "delete systemd units.."
rm -f /etc/systemd/system/${service}

echo "reloading configs.."
systemctl daemon-reload
udevadm control --reload-rules
