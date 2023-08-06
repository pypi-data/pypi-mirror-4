#!/bin/bash

i18ndude rebuild-pot --pot src/maahinkainen/portlet/googlecalendar/locales/maahinkainen.portlet.googlecalendar.pot --create maahinkainen.portlet.googlecalendar src/maahinkainen/portlet/googlecalendar

i18ndude sync --pot src/maahinkainen/portlet/googlecalendar/locales/maahinkainen.portlet.googlecalendar.pot src/maahinkainen/portlet/googlecalendar/locales/*/LC_MESSAGES/maahinkainen.portlet.googlecalendar.po
