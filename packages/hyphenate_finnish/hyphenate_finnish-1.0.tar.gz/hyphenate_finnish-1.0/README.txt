=================
Hyphenate Finnish
=================

By Pyry Kontio a.k.a Drasa (Drasa@IRCnet, pyry.kontio@drasa.eu)

A very simple hyphenator.
Hypenates Finnish text with Unicode soft hyphens. (U+00AD)
Allows to set margins for words so that they won't break right at start or end.
For example, it'd be a bit silly to break a word like 'erikoinen' at 'e-rikoinen'.
With default margin of 1, it breaks like 'eri-koinen'.

Usage:
as standalone script:

hypenate_finnish.py 2 joo joo no testaillaan täs vaa

OR as a Python module:

from hyphenate_finnish import hyphenate(text, margin=1)

It's that simple.
By the way, written with Py3k, but it seems to work with 2.7 too.
