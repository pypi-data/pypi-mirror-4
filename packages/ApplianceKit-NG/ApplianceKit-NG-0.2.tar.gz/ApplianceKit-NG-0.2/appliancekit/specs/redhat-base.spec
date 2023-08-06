{% extends "base.spec" %}
{% block bootstrap %}
	{"operation": "runcmd", "chroot": false, "command": ["rinse", "--distribution", "{{ distribution }}", "--directory", "$chroot", "--arch", "$debarch"]},
	{"operation": "render_template", "template": "base/resolv.conf.tmpl", "target": "/etc/resolv.conf"},
	{"operation": "runcmd", "chroot": true, "command": ["yum", "-y", "install", "authconfig"]},
	{"operation": "runcmd", "chroot": true, "command": ["authconfig", "--enableshadow", "--update"]},
	{"operation": "runcmd", "chroot": true, "command": ["chkconfig", "network", "on"]},
	{"operation": "runcmd", "chroot": true, "command": ["yum", "-y", "install", "kernel", "openssh-server", "sudo", "rootfiles"]},
	{"operation": "runcmd", "chroot": true, "command": ["chkconfig", "sshd", "on"]},
{% endblock %}
{% block packages %}
	{% for package in packages %}
		{"operation": "runcmd", "chroot": true, "command": ["yum", "-y", "install", "{{ package }}"]},
	{% endfor %}
{% endblock %}
{% block configure %}
	{{ super() }}
	{"operation": "render_template", "template": "redhat/HOSTNAME.tmpl", "target": "/etc/HOSTNAME"},
	{"operation": "render_template", "template": "redhat/sysconfig-network.tmpl", "target": "/etc/sysconfig/network"},
	{"operation": "render_template", "template": "redhat/sysconfig-network-ifcfg.tmpl", "target": "/etc/sysconfig/network-scripts/ifcfg-eth0"},
{% endblock %}
{% block xentweaks %}
	{{ super() }}
	{"operation": "render_template", "template": "redhat/grub-menu.lst.tmpl", "target": "/boot/grub/menu.lst"},
	{"operation": "runcmd", "chroot": true, "command": ["ln", "-sf", "/boot/grub/menu.lst", "/etc/grub.conf"]},
	{"operation": "render_template", "template": "redhat/xen-grubby-stub.tmpl", "target": "/sbin/xen-grubby-stub"},
	{"operation": "runcmd", "chroot": true, "command": ["sh", "/sbin/xen-grubby-stub"]},
	{"operation": "runcmd", "chroot": true, "command": ["rm", "/sbin/xen-grubby-stub"]},
{% endblock %}
{% block cleanup %}
{% endblock %}
