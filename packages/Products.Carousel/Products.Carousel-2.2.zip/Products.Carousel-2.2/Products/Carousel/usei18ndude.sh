#!/bin/bash 
DOMAIN="Products.Carousel"
PLONE="plone"
I18NDUDE=../../../../bin/i18ndude

# If you want to add another language create folders and empty file:
#   mkdir -p locales/<lang_code>/LC_MESSAGES
#   touch locales/<lang_code>/LC_MESSAGES/$DOMAIN.po
# and run this script
# Example: locales/hu/LC_MESSAGES/$DOMAIN.po

echo "Syncing all translations for domain ${DOMAIN}."
touch locales/$DOMAIN.pot
$I18NDUDE rebuild-pot --pot locales/$DOMAIN.pot --create $DOMAIN ./

# sync all locales
find locales -depth -type d   \
     | grep -v .svn \
     | grep -v LC_MESSAGES \
     | sed -e "s/locales\/\(.*\)$/\1/" \
     | xargs -I % $I18NDUDE sync --pot locales/${DOMAIN}.pot locales/%/LC_MESSAGES/${DOMAIN}.po

echo "Compile po files for domain ${DOMAIN}."
# Compile po files
for lang in $(find locales -mindepth 1 -maxdepth 1 -type d); do
    if test -d $lang/LC_MESSAGES; then
        msgfmt -o $lang/LC_MESSAGES/${DOMAIN}.mo $lang/LC_MESSAGES/${DOMAIN}.po
    fi
done

echo "Syncing all translations for domain plone."
#This is for the "plone" domain.

touch i18n/$DOMAIN-$PLONE.pot
$I18NDUDE rebuild-pot --pot i18n/$DOMAIN-$PLONE.pot --create $PLONE ./

$I18NDUDE sync --pot i18n/$DOMAIN-$PLONE.pot i18n/$DOMAIN-$PLONE-da.po
$I18NDUDE sync --pot i18n/$DOMAIN-$PLONE.pot i18n/$DOMAIN-$PLONE-es.po
$I18NDUDE sync --pot i18n/$DOMAIN-$PLONE.pot i18n/$DOMAIN-$PLONE-fi.po
$I18NDUDE sync --pot i18n/$DOMAIN-$PLONE.pot i18n/$DOMAIN-$PLONE-nl.po
