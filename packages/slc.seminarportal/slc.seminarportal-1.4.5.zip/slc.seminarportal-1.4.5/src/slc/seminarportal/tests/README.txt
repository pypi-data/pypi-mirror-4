Currently create_test_seminars fails due to monkey patching in
osha.policy/src/osha/policy/patches/linguaplone_defaultLanguage_patch.py
. osha.policy is not a dependency of slc.seminarportal, but
it is loaded via z3c.autoinclude. Disabling this

Z3C_AUTOINCLUDE_DEPENDENCIES_DISABLED=1; Z3C_AUTOINCLUDE_PLUGINS_DISABLED=1; instance test -s slc.seminarportal

causes it to be included via

osha/parts/instance/etc/package-includes/017-osha.adaptation-configure.zcml ,
osha/parts/instance/etc/site.zcml

I can't find a way to run this test cleanly from within an osha buildout.

