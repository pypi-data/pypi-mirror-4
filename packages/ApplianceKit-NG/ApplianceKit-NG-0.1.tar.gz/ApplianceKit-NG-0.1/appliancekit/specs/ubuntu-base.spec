{% extends "debian-base.spec" %}
{% block kernelinst %}
	{% if 'xen-tweaks' in phases %}
		{"operation": "runcmd", "chroot": true, "command": ["apt-get", "-y", "--force-yes", "install", "linux-virtual"]},
		{"operation": "runcmd", "chroot": true, "command": ["apt-get", "-y", "--force-yes", "install", "grub-legacy-ec2"]},
	{% else %}
		{{ super() }}
	{% endif %}
{% endblock %}
{% block xentweaks %}
	{"operation": "runcmd", "chroot": true, "command": ["sed", "-i", "s/defoptions=console=hvc0/defoptions=console=hvc0 rootflags=nobarrier/g", "/boot/grub/menu.lst"]},
	{"operation": "runcmd", "chroot": true, "command": ["sed", "-i", "s:kopt=root=/dev/hda1:kopt=root=/dev/xvda1:g", "/boot/grub/menu.lst"]},
	{"operation": "runcmd", "chroot": true, "command": ["update-grub-legacy-ec2"]},
	{"operation": "render_template", "template": "ubuntu/init-hvc0.tmpl", "target": "/etc/init/hvc0.conf"},
{% endblock %}
