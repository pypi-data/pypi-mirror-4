#!/bin/sh

DOMAIN1='collective.sortmyfolder'
i18ndude rebuild-pot --pot locales/${DOMAIN1}.pot --merge locales/${DOMAIN1}-manual.pot --create ${DOMAIN1} .
i18ndude sync --pot locales/${DOMAIN1}.pot locales/*/LC_MESSAGES/${DOMAIN1}.po
