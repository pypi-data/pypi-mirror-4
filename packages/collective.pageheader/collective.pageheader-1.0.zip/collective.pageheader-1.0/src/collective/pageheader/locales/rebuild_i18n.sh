#!/bin/sh
PRODUCTNAME='collective.pageheader'
I18NDOMAIN=$PRODUCTNAME

# Synchronise the .pot with the templates.
i18ndude rebuild-pot --pot ${PRODUCTNAME}.pot --merge ${PRODUCTNAME}-manual.pot --create ${I18NDOMAIN} .

# Synchronise the resulting .pot with the .po files
i18ndude sync --pot ${PRODUCTNAME}.pot */LC_MESSAGES/${PRODUCTNAME}.po


