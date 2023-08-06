#!/bin/bash
# kudos to Products.Ploneboard for the base for this file
# ensure that when something is wrong, nothing is broken more than it should...
set -e

# first, create some pot containing anything
i18ndude rebuild-pot --pot wpd.countdown.pot --create wpd.countdown --merge manual.pot ..

# finally, update the po files
i18ndude sync --pot wpd.countdown.pot  `find . -iregex '.*wpd.countdown\.po$'|grep -v plone`

# Generate .mo files
for po in `find . -name "*.po"` ; do msgfmt -o `dirname $po`/`basename $po .po`.mo $po; done
