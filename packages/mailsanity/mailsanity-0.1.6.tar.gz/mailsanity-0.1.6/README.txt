===========
Mail Sanity
===========

Mail Sanity provides modules for reformatting incoming mail.  You
might find it most useful coupled with rss2email, as many RSS feeds
provide much less information, than actually should be emailed, and
Mail Sanity fetch missing for you. Also, it makes best efford to
ensure nettiqette compliance of incoming email. For more details take
a look at futher sections. Typical usage often looks like following
rule in ``procmail``::

    :0:
    | ~/.local/bin/mailsanity

=============
Modules overview
=============

Module ``zovem``
=============

Module ``zovem`` exports function ``reformat``, that, given an email
message object, generated with ``rss2email`` and having header
``X-RSS-URL: http://www.zovem.ru/?event=12354``, fetch information
about event from http://zovem.ru and set body of given email. Also,
it prints a ``remind`` -- compatible reminder in body of email.



=============
Getting involved
=============

You are welcome to offer modules for another rss feeds.  Please, add a
few words about it into this README in your patch.
