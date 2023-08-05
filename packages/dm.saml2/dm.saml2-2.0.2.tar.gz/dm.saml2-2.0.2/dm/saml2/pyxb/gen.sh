# ensure envar PYXB_BASE points to the root of the `PyXB` installation.
#  Below it should be a `bundles` subdirectory.
PYXB_ARCHIVE_PATH=$PYXB_BASE/bundles/wsssplat/raw:$PYXB_BASE/bundles/saml20/raw

# authentication contexts (as they are)
#  do not work because 'xs:redefine' is used, unsupported by "PyXB 1.1.3".
#  The schemas for some contexts have been locally modified to avoid
#  'xs:redefine'. Should you need other contexts, the corresponding
#  schemas must be modified in similar fashion.
BASELOC=http://docs.oasis-open.org/security/saml/v2.0
MODLOC=modschema
pyxbgen  --write-for-customization --archive-to-file=raw/authncontext.wxs --binding-root=../../.. --archive-path=.:raw:$PYXB_ARCHIVE_PATH --module-prefix=dm.saml2.pyxb \
--schema-location=$BASELOC/saml-schema-authn-context-2.0.xsd --module=authncontext \
--schema-location=$MODLOC/saml-schema-authn-context-ip-2.0.xsd --module=authncontext_ip \
--schema-location=$MODLOC/saml-schema-authn-context-ippword-2.0.xsd --module=authncontext_ippword \
--schema-location=$MODLOC/saml-schema-authn-context-ppt-2.0.xsd --module=authncontext_ppt \
# not yet modified to avoid "xs:redefine"
#--schema-location=$BASELOC/saml-schema-authn-context-pword-2.0.xsd --module=authncontext_pword \
#--schema-location=$BASELOC/saml-schema-authn-context-session-2.0.xsd --module=authncontext_session \
#--schema-location=$BASELOC/saml-schema-authn-context-auth-telephony-2.0.xsd --module=authncontext_auth_telephony \
#--schema-location=$BASELOC/saml-schema-authn-context-kerberos-2.0.xsd --module=authncontext_kerberos \
#--schema-location=$BASELOC/saml-schema-authn-context-mobileonefactor-reg-2.0.xsd --module=authncontext_mobileonefactor_reg \
#--schema-location=$BASELOC/saml-schema-authn-context-mobileonefactor-unreg-2.0.xsd --module=authncontext_mobileonefactor_unreg \
#--schema-location=$BASELOC/saml-schema-authn-context-mobiletwofactor-reg-2.0.xsd --module=authncontext_mobiletwofactor_reg \
#--schema-location=$BASELOC/saml-schema-authn-context-mobiletwofactor-unreg-2.0.xsd --module=authncontext_mobiletwofactor_unreg \
#--schema-location=$BASELOC/saml-schema-authn-context-nomad-telephony-2.0.xsd --module=authncontext_nomad_telephony \
#--schema-location=$BASELOC/saml-schema-authn-context-personal-telephony-2.0.xsd --module=authncontext_personal_telephony \
#--schema-location=$BASELOC/saml-schema-authn-context-pgp-2.0.xsd --module=authncontext_pgp \
#--schema-location=$BASELOC/saml-schema-authn-context-smartcard-2.0.xsd --module=authncontext_smartcard \
#--schema-location=$BASELOC/saml-schema-authn-context-smartcardpki-2.0.xsd --module=authncontext_smartcardpki \
#--schema-location=$BASELOC/saml-schema-authn-context-softwarepki-2.0.xsd --module=authncontext_softwarepki \
#--schema-location=$BASELOC/saml-schema-authn-context-spki-2.0.xsd --module=authncontext_spki \
#--schema-location=$BASELOC/saml-schema-authn-context-srp-2.0.xsd --module=authncontext_srp \
#--schema-location=$BASELOC/saml-schema-authn-context-sslcert-2.0.xsd --module=authncontext_sslcert \
#--schema-location=$BASELOC/saml-schema-authn-context-telephony-2.0.xsd --module=authncontext_telephony \
#--schema-location=$BASELOC/saml-schema-authn-context-timesync-2.0.xsd --module=authncontext_timesync \
#--schema-location=$BASELOC/saml-schema-authn-context-types-2.0.xsd --module=authncontext_types \
#--schema-location=$BASELOC/saml-schema-authn-context-x509-2.0.xsd --module=authncontext_x509 \
#--schema-location=$BASELOC/saml-schema-authn-context-xmldsig-2.0.xsd --module=authncontext_xmldsig
