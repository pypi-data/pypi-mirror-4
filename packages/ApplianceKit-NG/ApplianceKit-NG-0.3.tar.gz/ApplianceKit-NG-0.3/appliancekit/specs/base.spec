{% block base %}
[
{% if 'bootstrap' in phases %}
{% block bootstrap %}
{% endblock %}
{% endif %}

{% if 'packages' in phases %}
{% block packages %}
{% endblock %}
{% endif %}

{% if 'custom' in phases %}
{% block custom %}
{% endblock %}
{% endif %}

{% if 'configure' in phases %}
{% block configure %}
	{"operation": "render_template", "template": "base/fstab.tmpl", "target": "/etc/fstab"},
{% endblock %}
{% endif %}

{% if 'xen-tweaks' in phases %}
{% block xentweaks %}
	{"operation": "runcmd", "chroot": true, "command": ["sed", "-i", "s:tty1:hvc0:g", "/etc/inittab"]},
{% endblock %}
{% endif %}

{% if 'cleanup' in phases %}
{% block cleanup %}
{% endblock %}
{% endif %}
	{"operation": "noop"}
]
{% endblock %}
