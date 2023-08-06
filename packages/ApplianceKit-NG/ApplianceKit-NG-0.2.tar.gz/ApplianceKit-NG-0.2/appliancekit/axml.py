#!/usr/bin/env python
"""
Copyright (c) 2008 SystemInPlace (parser)
Copyright (c) 2012, 2013 TortoiseLabs LLC

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

This software is provided 'as is' and without any warranty, express or
implied. In no event shall the authors be liable for any damages arising
from the use of this software.
"""

from appliancekit.compiler import compile_ir_string

import xml.parsers.expat
import urllib
import json

def get_appliancexml_from_xml_file(filepath):
    """Parse an XML file into an appliance config."""
    currentTag = []
    xmlConfig = {}

    def startTag(name, attrs):
        currentTag.append({'name': name, 'attrs': attrs})

    def endTag(name):
        currentTag.pop()

    def getTagPath():
        st = ""
        for tag in currentTag:
            if st != "":
                st += ".%s" % tag['name']
            else:
                st = tag['name']

        return st

    def characterData(data):
        if getTagPath() == "appliance.packagelist":
            pass
        elif getTagPath() == "appliance.packagelist.package":
            try:
                xmlConfig[ "appliance.packagelist" ].append(data)
            except:
                xmlConfig[ "appliance.packagelist" ] = [ data ]
        elif getTagPath() == "appliance.scriptlet.preinstall":
            try:
                xmlConfig[ "appliance.scriptlet.preinstall" ].append(data)
            except:
                xmlConfig[ "appliance.scriptlet.preinstall" ] = [ data ]
        elif getTagPath() == "appliance.scriptlet.postinstall":
            try:
                xmlConfig[ "appliance.scriptlet.postinstall" ].append(data)
            except:
                xmlConfig[ "appliance.scriptlet.postinstall" ] = [ data ]
        else:
            xmlConfig[ getTagPath() ] = data

    f = urllib.URLopener().open(filepath)
    data = f.read()
    f.close()

    p = xml.parsers.expat.ParserCreate()
    p.StartElementHandler = startTag
    p.EndElementHandler = endTag
    p.CharacterDataHandler = characterData
    p.Parse(data)

    return xmlConfig

def get_appliance_config_from_xml_file(filepath):
    xmlConfig = get_appliancexml_from_xml_file(filepath)
    
    config = {}

    try:    
        config['packageList'] = xmlConfig['appliance.packagelist']
    except:
        config['packageList'] = []

    try:
        config['scriptlet.preinstall'] = xmlConfig['appliance.scriptlet.preinstall']
    except:
        config['scriptlet.preinstall'] = []

    try:
        config['scriptlet.postinstall'] = xmlConfig['appliance.scriptlet.postinstall']
    except:
        config['scriptlet.postinstall'] = []

    config['distribution'] = xmlConfig['appliance.distribution']

    return config

def translate_axml_file(filepath):
    axmlconfig = get_appliance_config_from_xml_file(filepath)
    distMap = {
	'lenny': 'debian-5',
	'squeeze': 'debian-6',
	'wheezy': 'debian-7',
	'sid': 'debian-base',

	'lucid': 'ubuntu-10.04',
    }

    def get_distname(name):
        if distMap.has_key(name):
            return distMap[name]
        return name

    trans = '{% extends "' + get_distname(axmlconfig['distribution']) + '.spec" %}\r\n'
    if axmlconfig.has_key('packageList') and len(axmlconfig['packageList']) > 0:
        trans += "{% " + "set packages={}".format(json.dumps(axmlconfig['packageList'])) + " %}\r\n"

    return trans

def compile_axml_file(filepath, **kwargs):
    trans_ir = translate_axml_file(filepath)
    weaved_ir = compile_ir_string(trans_ir, **kwargs)
    return json.loads(weaved_ir)
