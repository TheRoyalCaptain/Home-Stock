#!/bin/sh
set -eu
mkdir -p /run/cups /var/spool/cups /var/log/cups
rm -f /run/cups/cups.sock /run/cups/cupsd.pid
/usr/sbin/cupsd
exec gunicorn --bind 0.0.0.0:8631 --workers 1 --threads 2 --timeout 60 printer_service:app
