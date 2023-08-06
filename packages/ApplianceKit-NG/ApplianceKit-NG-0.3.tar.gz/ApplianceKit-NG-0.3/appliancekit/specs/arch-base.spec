{% extends "base.spec" %}
{% set paths=['/tmp', '/sys', '/dev', '/run', '/etc', '/proc', '/var/cache/pacman/pkg', '/var/lib/pacman', '/var/log'] %}
{% set bindmounts=['/dev', '/proc', '/sys'] %}
{% block bootstrap %}
	{% for path in paths %}
		{"operation": "mkdir_p", "path": "{{ path }}"},
	{% endfor %}
	{"operation": "render_template", "template": "arch/pacman-bootstrap.conf.tmpl", "target": "/etc/pacman-bootstrap.conf"},
	{% for path in bindmounts %}
		{"operation": "runcmd", "chroot": false, "command": ["mount", "-o", "bind", "{{ path }}", "$chroot/{{ path }}"]},
	{% endfor %}
	{"operation": "runcmd", "chroot": false, "command": ["pacman", "-Syu", "--root", "$chroot", "--config", "$chroot/etc/pacman-bootstrap.conf", "--noconfirm", "base"]},
	{"operation": "render_template", "template": "arch/pacman-full.conf.tmpl", "target": "/etc/pacman.conf"},
	{"operation": "render_template", "template": "arch/mirrorlist.tmpl", "target": "/etc/pacman.d/mirrorlist"},
	{"operation": "render_template", "template": "base/resolv.conf.tmpl", "target": "/etc/resolv.conf"},
	{"operation": "runcmd", "chroot": true, "command": ["pacman", "-Sy", "--noconfirm", "openssh"]},
	{"operation": "runcmd", "chroot": true, "command": ["ln", "-sf", "/usr/lib/systemd/system/sshd.service", "/etc/systemd/system/multi-user.target.wants/sshd.service"]},
	{"operation": "render_template", "template": "arch/grub-menu.lst.tmpl", "target": "/boot/grub/menu.lst"},
	{% for path in bindmounts %}
		{"operation": "runcmd", "chroot": false, "command": ["umount", "$chroot/{{ path }}"]},
	{% endfor %}
{% endblock %}
{% block packages %}
	{% for package in packages %}
		{"operation": "runcmd", "chroot": true, "command": ["pacman", "-Sy", "--noconfirm", "{{ package }}"]},
	{% endfor %}
{% endblock %}
{% block configure %}
	{{ super() }}
	{"operation": "render_template", "template": "arch/network.service.tmpl", "target": "/etc/systemd/system/multi-user.target.wants/network.service"},
	{"operation": "render_template", "template": "debian/hostname.tmpl", "target": "/etc/hostname"},
{% endblock %}
{% block cleanup %}
{% endblock %}
