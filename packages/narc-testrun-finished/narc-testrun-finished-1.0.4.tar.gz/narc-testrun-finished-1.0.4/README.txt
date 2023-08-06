===============================
 Narc Testrun Finished Plugin
===============================

Normally when testruns in slick (http://code.google.com/p/slickqa) are finished, the program
that uploaded the results marks the testrun as finished.  This is not possible in some
scenarios, including when doing distributed testing.

This plugin watches testrun updates, and whenever a testrun that had NO_RESULT results no
longer has NO_RESULT results, it marks the testrun as finished.  This will trigger the
emails in narc.
