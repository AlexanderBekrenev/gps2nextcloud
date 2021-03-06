## Description

This is simple gate tcp server between GPS tracker devices and Nextcloud PhoneTrack application (https://gitlab.com/eneiluj/phonetrack-oc).

Description of the protocols and work with the trackers borrowed from the project Traccar (https://traccar.org & https://github.com/traccar/traccar)

Protocols link: https://www.traccar.org/protocols/

Currently implemented _watch_ and _H02_ protocol only.

### Install

Installation process described for Ubuntu 18.04

Download archive file with latest version\
https://github.com/AlexanderBekrenev/gps2nextcloud/raw/master/dist/gps2nextcloud-0.1.8.tar.gz

Install to system scheme: \
`sudo pip3 install --system gps2nextcloud-0.1.8.tar.gz`

Make initial install: \
`sudo gps2nextcloud-install `

Edit initial config file '/etc/gps2nextcloud/gps2nextcloud.ini' and change Nextcloud server name and `YOUR_SESSION_TOKEN` to real token value from Nextcloud PhoneTrace application

### Run as systemd daemon

Create service file
`/etc/systemd/system/gps2nextcloud.service`
```
[Unit]
Description=GPS Trackers to NextCloud PhoheTrack TCP gate
After=multi-user.target
[Service]
Type=idle
ExecStart=/usr/bin/python3 /usr/local/lib/python3.6/dist-packages/gps2nextcloud/server.py --config_file /etc/gps2nextcloud/gps2nextcloud.ini
Restart=always
StandardOutput=syslog
StandardError=syslog

[Install]
WantedBy=multi-user.target
```
Check ExecStart line for your paths.

Start daemon: `systemctl start gps2nextcloud`

Enable daemon `systemctl enable gps2nextcloud`

Stop daemon: `systemctl stop gps2nextcloud`

Disable daemon `systemctl disable gps2nextcloud`

Check daemon status: `systemctl status gps2nextcloud`

### Update
If you already have gps2nextcloud installed and working and you want to update the version, 
then you need to do the following:

- Download new version (change x.x.x to version number)
```sh
wget https://github.com/AlexanderBekrenev/gps2nextcloud/raw/master/dist/gps2nextcloud-x.x.x.tar.gz
```
- Uninstall old version
```shell script
sudo pip3 uninstall gps2nextcloud
```
It does not affect your ini-file.

- Install new version
```shell script
sudo pip3 install --system gps2nextcloud-0.1.8.tar.gz
```

- Restart daemon if you use it.
```shell script
sudo systemctl restart gps2nextcloud
```

- Check daemon status
```shell script
sudo systemctl status gps2nextcloud
```
It is show something like this:
```text
 gps2nextcloud.service - GPS Trackers to NextCloud PhoheTrack TCP gate
   Loaded: loaded (/etc/systemd/system/gps2nextcloud.service; enabled; vendor preset: enabled)
   Active: active (running) since Fri 2019-08-30 22:14:09 MSK; 6s ago
 Main PID: 32119 (python3)
    Tasks: 2 (limit: 4915)
   CGroup: /system.slice/gps2nextcloud.service
           ├─32119 /usr/bin/python3 /usr/local/lib/python3.6/dist-packages/gps2nextcloud/server.py --config_file /etc/gps2nextcloud/gps2nextcloud.ini
           └─32159 /usr/bin/python3 /usr/local/lib/python3.6/dist-packages/gps2nextcloud/server.py --config_file /etc/gps2nextcloud/gps2nextcloud.ini

авг 30 22:14:09 blackrock systemd[1]: Started GPS Trackers to NextCloud PhoheTrack TCP gate.
авг 30 22:14:09 blackrock python3[32119]: [INFO/gps2nextcloud_DummyGate] child process calling self.run()
авг 30 22:14:09 blackrock python3[32119]: [INFO/gps2nextcloud_WatchGate] child process calling self.run()
авг 30 22:14:09 blackrock python3[32119]: [INFO/gps2nextcloud_DummyGate] listening on localhost:5009
```
###### Changes

[Change file](CHANGES.md)
