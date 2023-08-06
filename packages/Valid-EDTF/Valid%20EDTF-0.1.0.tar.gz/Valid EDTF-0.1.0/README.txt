==========
VALID EDTF
==========

Valid EDTF provides validity testing against EDTF levels 1-3. You might find
it most useful for tasks involving date validation and comparison. Typical usage
often looks like this::

    #!/usr/bin/env python

    from towelstuff import isLevel1

    if isLevel1(edtf_candidate):
        print "The date, %s, is level 1 edtf validated" % edtf_candidate


EDTF specification can be viewed `here <http://www.loc.gov/standards/datetime/pre-submission.html>`_.

