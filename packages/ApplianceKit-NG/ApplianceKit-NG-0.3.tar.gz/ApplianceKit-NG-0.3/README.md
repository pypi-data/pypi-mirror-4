# appliancekit-ng

Copyright (c) 2012, 2013 TortoiseLabs, LLC.

This software is free but copyrighted, see COPYING.md for more details.

## motive

ApplianceKit has become unmaintainable.  In addition, it depends on XML and exposes too much
implementation details in the Python-based core.

By using an intermediate representation between the XML and what actually happens, it is
possible to:

* Implement all logic for bringing up a distribution as data, by using a stack machine
  to interpret the data.

* Add new distributions by writing specfiles for them instead of entirely new classes of
  monolithic code in Python.

* Eventually transition away entirely from using AXML.

## intermediate representation

Most of what the ApplianceKit NG core does is:

* Translate XML into IR, for example an XML file might be translated into this high-level IR,
  which will get compiled into lower-level IR.

```
{% extends "debian-6.spec" %}
{% set packages=['irssi'] %}
```

* Translate high-level IR into low-level IR using translation rules as described in the base
  specfiles.  You can use ak-compile or ak-compile-xml to view what the lowlevel IR parsetree
  looks like.

* Compile a parse tree into bytecode and then run the bytecode to create the appliance
  filesystem.

For more information on the IR language, see [ADL.md](ADL.md).

## requirements

* For Alpine: `apk-tools`.
* For Debian or Ubuntu: `debootstrap`.
* For CentOS, ScientificLinux, RHEL, openSUSE: `rinse`.

