Frequently Asked Questions
==========================

- Is there a list of all messages?

  - No, not yet.  The best lists are the unit tests of the Fedora Infrastructure
    `fedmsg.meta plugin
    <https://github.com/fedora-infra/fedmsg_meta_fedora_infrastructure>`_.  You
    should check `this file <https://github.com/fedora-infra/fedmsg_meta_fedora_infrastructure/blob/develop/fedmsg_meta_fedora_infrastructure/tests/__init__.py>`_ and `this file <https://github.com/fedora-infra/fedmsg_meta_fedora_infrastructure/blob/develop/fedmsg_meta_fedora_infrastructure/tests/pkgdb.py>`_.  We do need a document listing them, explaining them briefly, and providing an example of message content.  If you'd like to help start that project, it would be an excellent place to contribute (please report any progress `here <https://github.com/fedora-infra/fedmsg/issues/117>`_).

- When will we be getting koji messages?

  - We got them in late January, 2013!  Look for
    ``org.fedoraproject.prod.buildsys...``

- When will we be getting bugzilla messages?

  - Not for a while, unfortunately.  We're waiting on Red Hat to sort out issues
    on their end with qpidd.

- Can I deploy fedmsg at my site, even if it has nothing to do with Fedora?

  - Yes.  It was designed so that all the Fedora-isms could be separated out
    into plugins.  Get in touch with ``#fedora-apps`` or create a ticket if
    you'd like to try this out.
