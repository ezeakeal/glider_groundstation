#!/usr/bin/env bash
set -e

####################
# CONFIGURATION
####################
DESIRED_WIFI_NETWORK="groundstation"
WIRELESS_DEVICE=wlan0
####################

function scan_for_wifi {
    echo "Scanning for Wifi network: $DESIRED_WIFI_NETWORK"
    sudo iw dev $WIRELESS_DEVICE scan ap-force ssid | grep SSID | grep $DESIRED_WIFI_NETWORK
    return $?
}

function connect_wifi {
    echo "--------------------------"
    echo "CONNECTING to Wifi network"
    echo "--------------------------"
    sudo iwconfig $WIRELESS_DEVICE essid $DESIRED_WIFI_NETWORK
    sudo dhclient $WIRELESS_DEVICE
}

function create_adhoc {
    echo "--------------------------"
    echo "CREATING AD-HOC Wifi network"
    echo "--------------------------"
    sudo /etc/init.d/hostapd start
    sudo /usr/local/bin/hotspotd start
    echo "Ad-hoc network created"
}

sudo /usr/local/bin/hotspotd stop
sudo /etc/init.d/hostapd stop
sudo ifconfig $WIRELESS_DEVICE up
if scan_for_wifi; then
    echo "Wifi network '$DESIRED_WIFI_NETWORK' found"
    connect_wifi
else
    echo "Wifi network not found, creating ad-hoc groundstation network"
    create_adhoc
fi

