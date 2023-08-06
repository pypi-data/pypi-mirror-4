{% extends "base.spec" %}
{% set boot_svcs=['bootmisc', 'hostname', 'hwclock', 'modules', 'sysctl', 'syslog'] %}
{% set sysinit_svcs=['devfs', 'dmesg', 'hwdrivers', 'mdev', 'modloop'] %}
{% set shutdown_svcs=['killprocs', 'mount-ro', 'savecache'] %}
{% set default_svcs=['networking', 'sshd'] %}
{% block bootstrap %}
	{"operation": "runcmd", "chroot": false, "command": ["apk", "--initdb", "--root", "$chroot", "add"]},
	{"operation": "runcmd", "chroot": false, "command": ["apk", "-X", "http://nl.alpinelinux.org/alpine/{{ distribution }}/main", "--allow-untrusted", "--root", "$chroot", "update"]},
	{"operation": "runcmd", "chroot": false, "command": ["apk", "-X", "http://nl.alpinelinux.org/alpine/{{ distribution }}/main", "--allow-untrusted", "--root", "$chroot", "add", "alpine-base", "alpine-mirrors"]},
	{"operation": "render_template", "template": "base/resolv.conf.tmpl", "target": "/etc/resolv.conf"},
	{"operation": "runcmd", "chroot": true, "command": ["setup-apkrepos", "-r"]},
	{"operation": "runcmd", "chroot": true, "command": ["apk", "add", "openssh", "e2fsprogs", "linux-grsec"]},
	{% for service in boot_svcs %}
		{"operation": "runcmd", "chroot": true, "command": ["rc-update", "add", "{{ service }}", "boot"]},
	{% endfor %}
	{% for service in sysinit_svcs %}
		{"operation": "runcmd", "chroot": true, "command": ["rc-update", "add", "{{ service }}", "sysinit"]},
	{% endfor %}
	{% for service in shutdown_svcs %}
		{"operation": "runcmd", "chroot": true, "command": ["rc-update", "add", "{{ service }}", "shutdown"]},
	{% endfor %}
	{% for service in default_svcs %}
		{"operation": "runcmd", "chroot": true, "command": ["rc-update", "add", "{{ service }}", "default"]},
	{% endfor %}
	{"operation": "render_template", "template": "alpine/grub-menu.lst.tmpl", "target": "/boot/grub/menu.lst"},
{% endblock %}
{% block packages %}
	{% for package in packages %}
		{"operation": "runcmd", "chroot": true, "command": ["apk", "add", "--force", "--allow-untrusted", "{{ package }}"]},
	{% endfor %}
{% endblock %}
{% block configure %}
	{{ super() }}
	{"operation": "render_template", "template": "debian/interfaces.tmpl", "target": "/etc/network/interfaces"},
	{"operation": "render_template", "template": "debian/hostname.tmpl", "target": "/etc/hostname"},
{% endblock %}
{% block cleanup %}
{% endblock %}
