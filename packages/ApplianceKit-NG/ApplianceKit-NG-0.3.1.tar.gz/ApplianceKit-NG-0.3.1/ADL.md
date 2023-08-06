# Appliance Definition Language specification

ADL is an abstract parse-tree expressed in JSON.  Each node in the tree has a mandatory
`operation` property.  All other fields in the nodes are sub-properties.

A tree node looks like this:

```
{"operation": "runcmd", "chroot": true, "command": ["/bin/true"]}
```

We use [Jinja2](http://jinja.pocoo.org) as a preprocessor.  This provides a useful macro
language, which we have built a framework around.  The rest of this document concerns the
macro system and operations.

`base.spec` defines a root of an ADL parse tree, as well as some hooks for various phases
which may be reimplemented downstream by users of `base.spec`.  Almost all ADL files should
derive from `base.spec`, which is declared by doing the following:

```
{% extends "base.spec" %}
```

## Operations

There are various operations which are implemented by the interpreter.  They are:

* **runcmd**: Run a command inside or outside of a chroot.  Takes two parameters, **chroot**
  which is a boolean, and **command** which contains the arguments and command name.

* **render_template**: Renders a template and installs it to a location in the guest filesystem.

* **noop**: Skips this node in the parse tree.

## Phases

There are various phases which are implemented by `base.spec`.  This allows for ADL files
built ontop of the framework provided by `base.spec` to weave only certain parse tree
nodes into the final parse tree representation based on what the end-user wants to do.

These phases are encapsulated inside `{% block %}` constructs.

The phases are:

* **bootstrap**: Commands to get an initial system installed.  Things like `debootstrap` and
  `pacstrap`.  Perhaps ugly hacks involving rpm2cpio, but we will probably ship a helper script
  for that.

* **packages**: Commands to install user specified packages or otherwise optional packages that
  are not needed in the system when it's done with the **bootstrap** phase, but would be needed
  to bring the system up on a hypervisor or under bare metal.

* **configuration**: Commands to set up the configuration of the appliance based on the `config`
  object.

* **custom**: Any special commands that the specfile may wish to provide.  Also could have additional
  phases here.

* **cleanup**: Cleans up any changes done to the guest filesystem during **bootstrap**.

* **xentweaks**: Tweaks some config files for running under Xen, such as `/etc/inittab`.

