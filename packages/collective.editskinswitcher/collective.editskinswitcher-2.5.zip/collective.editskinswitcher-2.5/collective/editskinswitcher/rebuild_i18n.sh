#!/bin/bash
# Run this script to update the translations.
i18ndude rebuild-pot --pot locales/editskinswitcher.pot --create editskinswitcher .
i18ndude sync --pot locales/editskinswitcher.pot $(find . -name 'editskinswitcher.po')
