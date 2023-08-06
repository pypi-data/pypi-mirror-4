.. contents::

rebecca.todict_bpmappers
===============================

``rebecca.todict_bpmappers`` is implementation for `rebecca.todict <http://pypi.python.org/pypi/rebecca.todict/>`_
using `bpmappers <http://pypi.python.org/pypi/bpmappers/>`_

INSTALL
==================

Install using pip or easy_install.::

  $ pip install rebecca.todict_bpmappers
  $ easy_install rebecca.todict_bpmappers


USAGE
===============

``rebecca.todict_bpmappers`` has include hook.::

  config.include('rebecca.todict_bpmappers')

This hook will include ``rebecca.todict`` too.

``bpmapper`` decorator register todict adapter implemented by ``bpmappers``.

::

  from bpmappers import Mapper, RawField
  from rebecca.todict_bpmappers import bpmapper

  @bpmapper('dummy.Person', name="p1")
  class PersonMapper(Mapper):
      username = RawField('name')
      num = RawField('value')

To use that mapper, call ``todict`` API of `rebecca.todict`::

  d = todict(request, person, name="p1")


