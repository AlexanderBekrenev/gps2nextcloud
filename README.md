Description
===========
This is simple gate tcp server between GPS tracker devices and Nextcloud PhoneTrack application (https://gitlab.com/eneiluj/phonetrack-oc).

Description of the protocols and work with the trackers borrowed from the project Traccar (https://traccar.org & https://github.com/traccar/traccar)

Protocols link: https://www.traccar.org/protocols/

Currently implemented _watch_ protocol only.
Version 0.1.8 has implementation for _H02_ protocol but it does not tested on real tracker.

Install
=======
Installation process described for Ubuntu 18.04

Download archive file with latest version\
https://github.com/AlexanderBekrenev/gps2nextcloud/raw/master/dist/gps2nextcloud-0.1.8.tar.gz

Install to system scheme: \
`sudo pip3 install --system gps2nextcloud-0.1.8.tar.gz`

Make initial install: \
`sudo gps2nextcloud-install `

Edit initial config file '/etc/gps2nextcloud/gps2nextcloud.ini' and change Nextcloud server name and `YOUR_SESSION_TOKEN` to real token value from Nextcloud PhoneTrace application

Run as systemd daemon
=====================
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


Changes
-------

Change file (CHANGES.md)
