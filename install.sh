#!/bin/bash
set -e

KLIPPER_PATH="${HOME}/klipper"
SYSTEMDDIR="/etc/systemd/system"

check_klipper()
{
    if [ "$(sudo systemctl list-units --full -all -t service --no-legend | grep -F "klipper.service")" ]; then
        echo "Klipper service found!"
    else
        echo "Klipper service not found, please install Klipper first"
        exit -1
    fi
}

link_plugin()
{
    echo "Linking extension to Klipper..."
    ln -sf "${SRCDIR}/heatsoak.py" "${KLIPPER_PATH}/klippy/extras/heatsoak.py"
}

install_systemd_unit()
{
    SERVICE_FILE="${SYSTEMDDIR}/heatsoak.service"
    if [ -f $SERVICE_FILE ]; then
        sudo rm "$SERVICE_FILE"
    fi

    echo "Installing systemd unit..."
    sudo /bin/sh -c "cat > ${SERVICE_FILE}" << EOF
[Unit]
Description=Dummy Service for heatsoak plugin
After=klipper.service
[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/bash -c 'exec -a heatsoak sleep 1'
ExecStopPost=/usr/sbin/service klipper restart
TimeoutStopSec=1s
[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable heatsoak.service
}

restart_klipper()
{
    echo "Restarting Klipper..."
    sudo systemctl restart klipper
}

verify_ready()
{
    if [ "$EUID" -eq 0 ]; then
        echo "This script must not run as root"
        exit -1
    fi
}

# Determine location of this script
SRCDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/ && pwd )"

while getopts "k:" arg; do
    case $arg in
        k) KLIPPER_PATH=$OPTARG;;
    esac
done

# Run steps
verify_ready
link_plugin
install_systemd_unit
restart_klipper