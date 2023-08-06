# -*- coding: utf-8 -*-
import pyramid.settings
import pyramid.config

checkmark = b'\xe2\x9c\x93'.decode('utf-8')
bold_check = b'\xe2\x9c\x94'.decode('utf-8')

truthy = frozenset(('t', 'true', 'y', 'yes', 'on', '1', checkmark, bold_check))

def asbool(txt):
    """ Return the boolean value ``True`` if the case-lowered value of string
    input ``txt`` is any of ``t``, ``true``, ``y``, ``on``, ``1``, or '✔'
    otherwise return the boolean value ``False``.  If ``txt`` is the value
    ``None``, return ``False``.  If ``txt`` is already one of the boolean values
    ``True`` or ``False``, return it."""

    if txt is None:
        return False

    if isinstance(txt, bool):
        return txt

    if hasattr(txt, 'decode'):
        try:
            txt = txt.decode('utf-8')
        except UnicodeEncodeError:
            pass
    else:
        txt = str(txt).strip()

    return txt.lower() in truthy

def patch_asbool():
    modules_to_patch= [pyramid.settings, pyramid.config.settings]

    pyramid.settings.truthy = truthy

    for mod in modules_to_patch:
        mod.asbool = asbool
