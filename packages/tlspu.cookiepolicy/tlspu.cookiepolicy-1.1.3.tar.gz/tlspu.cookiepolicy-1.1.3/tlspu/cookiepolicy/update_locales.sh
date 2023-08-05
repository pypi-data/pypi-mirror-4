#! /bin/sh

I18NDOMAIN="tlspu.cookiepolicy"

# Synchronise the templates and scripts with the .pot.
i18ndude rebuild-pot --pot locales/${I18NDOMAIN}.pot --create ${I18NDOMAIN} .

# Synchronise the resulting .pot with all .po files
for po in locales/*/LC_MESSAGES/${I18NDOMAIN}.po; do
    i18ndude sync --pot locales/${I18NDOMAIN}.pot $po
done
