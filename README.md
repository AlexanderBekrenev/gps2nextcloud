Description
===========
This is simple gate tcp server between GPS tracker devices and NextCloud PhoneTrack application (https://gitlab.com/eneiluj/phonetrack-oc).

Description of the protocols and work with the trackers borrowed from the project Traccar (https://traccar.org & https://github.com/traccar/traccar)

Protocols link: https://www.traccar.org/protocols/

Currently implemented _watch_ protocol only.

Install
=======
Install ation process described for Ubuntu 18.04

Download archive file with latest version\
`gps2nextcloud-0.1.0.tar.gz`

Install to system scheme: \
`sudo pip3 install --system gps2nextcloud-0.1.0.tar.gz`

Make initial install: \
`sudo gps2nextcloud-install `

Edit initial config file '/etc/gps2nextcloud/gps2nextcloud.ini' and change `YOUR_SESSION_TOKEN` to real token value from Nextcloud PhoneTrace application


[]: https://www.traccar.org/protocols/