domain=cooptation
i18ndude rebuild-pot --pot locales/$domain.pot --create $domain --merge i18n/generated.pot .
i18ndude sync --pot locales/$domain.pot locales/*/LC_MESSAGES/$domain.po

i18ndude rebuild-pot --pot locales/plone.pot --create plone profiles
i18ndude filter locales/plone.pot ../../../plone.app.locales/plone/app/locales/locales/plone.pot > locales/plone.pot_
mv locales/plone.pot_ locales/plone.pot
i18ndude sync --pot locales/plone.pot i18n/$domain-plone-fr.po
