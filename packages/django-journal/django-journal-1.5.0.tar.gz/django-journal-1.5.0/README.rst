Journal application
===================

Log event to a journal. Keep details of the event linked to the event message,
keep also the template for displaying the event in case we want to improve
display.

To use just do::

      import django_journal
      django_journal.record('my-tag', '{user} did this to {that}',
                 user=request.user, that=model_instance)


Admin display
-------------

``admin.JournalModelAdmin`` recompute messages from the journal message as HTML
adding links for filtering by object and to the ``change`` admin page for the
object if it has one.

Recording error events
----------------------

If you use transactions you must use ``error_record()`` instead of
``record()`` and set ``JOURNAL_DB_FOR_ERROR_ALIAS`` in your settings to
define another db alias to use so that journal record does not happen
inside the current transaction.
