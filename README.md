# dust-sensor
PPD42 -> Raspberry Pi -> HTTP (WiFi/Flask)

## Raspberry PI 2
- Install Raspian

### Network Configuration
- Plug-In a USB-WiFi Dongle that works with the Raspberry PI
- Edit `/etc/network/interfaces` to configure a static ip (And a low-prio route if both interfaces - `eth0` and `wlan0` - are connected):

```
...
allow-hotplug wlan0
iface wlan0 inet static
    address 192.168.43.50
    netmask 255.255.255.0
    post-up route add default gw 192.168.43.1 metric 500
    pre-down route del default gw 192.168.43.1
    wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf
```

- Edit `/etc/wpa_supplicant/wpa_supplicant.conf` to configure the WiFi:

```
...
network={
    ssid="xxx"
    psk="xxx"
}
```

- Configure a static DNS-Server in `/etc/resolv.conf.head`:

```
nameserver 8.8.8.8
```

- Disable DHCP for `wlan0` in `/etc/dhcpcd.conf`:

```
denyinterfaces wlan0
```
### Timezone
- Set the correct timezone with: `sudo dpkg-reconfigure tzdata`

### Supervisord
- Install: `sudo apt-get install supervisor`
- create config `/etc/supervisor/conf.d/dustsensor.conf`:

```
[program:dustsensor]
command=/home/pi/dustsensor/serve.py
autostart=true
autorestart=true
stderr_logfile=/home/pi/dustsensor/serve.stderr
stdout_logfile=/home/pi/dustsensor/serve.stdout
```
- `sudo systemctl enable supervisor`
- `sudo systemctl start supervisor`
- `sudo supervisorctl reread`
- `sudo supervisorctl update`

## PPD42
- Compile `dustsensor.c` (described in the file itself)
