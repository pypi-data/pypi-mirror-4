Changelog for collective.emaillogin
===================================


1.3 (2012-09-24)
----------------

- Avoid possible circular import for the PloneMembershipTool in
  PlonePAS and CMFPlone.
  [maurits]

- Moved to https://github.com/collective/collective.emaillogin
  [maurits]


1.2 (2012-02-14)
----------------

- Patch RegistrationTool.isMemberIdAllowed.  When the id that is
  passed in is already in use as login name, we do not accept it as
  user id either.  Also, in various spots where isMemberIdAllowed is
  called, the id is really meant as login name.
  Possibly this fix is only needed for Plone 3.1 and earlier, as I am
  sure I have tested this before on Plone 3.3.6.
  [maurits]

- Patch the login method from
  Products.PlonePAS.plugins.cookie_handler.ExtendedCookieAuthHelper.
  This is the code from Plone 3.3.6; it is included because Plone 3.1.7
  does the wrong thing for us here.
  [maurits]


1.1 (2011-12-13)
----------------

- Patch CMFPlone.MembershipTool.testCurrentPassword to authenticate
  with the login name.  The code in Plone 3.3.5 itself already works
  (and is simply copied here), but Plone 3.1.7 has an error that is
  triggered for us as the user id is not always the same as the login
  name.
  [maurits]


1.0 (2011-11-23)
----------------

- In the mailPassword method explicitly disallow looking for a member
  with the given forgotten user id when this is an e-mail address.  We
  only search for users with that e-mail address as login name.  This
  only has an effect when you have changed your e-mail address to
  something really different (instead of just a change in the case).
  Without this change, you could reset your password with your old
  address, but could not login with that address.
  [maurits]

- Refactored authenticateCredentials.  This avoids getting a message
  stating you are logged in when in fact you are not logged in.
  [maurits]

- Added upgrade step to migrate all existing users to have a lowercase
  login name (when their e-mail address is used as login name).
  [maurits]

- Patch PloneTool.setMemberProperties to always set the e-mail address
  to lower case and to update the login name when the e-mail address
  changes.
  [maurits]

- In validate_personalize.vpy turn the e-mail address to lowercase.
  [maurits]

- Patch Products.PlonePAS.tools.membership.MembershipTool.addMember to
  always add the member as lowercase, also when not called from
  registered.cpy
  [maurits]

- In join_form_validate.vpy turn the e-mail address to lowercase.
  [maurits]

- Changed getMemberByLoginName and ZODBUserManager.authenticateCredentials
  to explicitly search for the lower case login name if the initial
  literal search does not work.
  [maurits]

- Added classifiers for Plone 3.2 and 3.3 in setup.py.
  [maurits]


0.8 (2010-05-18)
----------------

- Removed mail_me functionality from join_form as this claimed to be
  sending the password, which Plone has not been doing for a long
  time, if ever.  The backend handling for this was already removed
  from Plone itself.
  [maurits]

- Fixed wrong condition and double definition where allowEnterPassword
  meant you were actually *not* allowed to enter a password.  It
  worked fine but was confusingly stated the wrong way around.
  [maurits]


0.7 (2010-02-23)
----------------

- added german translation [deichi]


0.6 (2009-05-13)
----------------

- Patched some methods in PasswordResetTool and RegistrationTool to
  make sure you can actually reset your password, even after changing
  your email address.  [maurits]

- Use email address instead of login/user name in some more spots,
  like the login form and in validation.  [maurits]


0.5 (2009-05-06)
----------------

- Fixed error on reinstall where the default skin would be set to the
  no longer existing emaillogin skin.  [maurits]

- Added profiles/default/metadata.xml: version = 1.  [maurits]

- After a successfull edit of the personalize form, do not travere to
  the personalize_form, but redirect to it.  This solves an error
  "Forbidden: Form authenticator is invalid." when changing your email
  address (= login name) and then saving the form a second time.
  [maurits]

- Changed validate_personalize.vpy to allow changing your preferences
  again.  [maurits]

- Adapted validate_personalize.vpy.  Change compared to default Plone:
  check the validity of the email address as a login name.  [maurits]

- Added i18n.  [maurits]


0.4 (2009-05-05)
----------------

- Also show the error when the email address is not a valid username.
  [maurits+mike]


0.3 (2009-05-05)
----------------

- Removed personalize_form.cpt(.metadata) as there was no important
  difference with the one from default Plone.  [maurits+mike]

- Take over a small change in default Plone to the personalize.cpy.

- Fixed join form to also work in newer Plones by using the
  @@authenticator provider for protecting this join form.  Keeps
  working in Plone 3.0 as well (which does not use plone.protect).
  [maurits+mike]


0.2 (2009-05-05)
----------------

- No longer register our own skin path (skin selection), but just add
  our emaillogin skin layer to the existing skin selections.
  [maurits+mike]


0.1 (2008-01-15)
----------------

- Initial release.
  [maurits, guido]

