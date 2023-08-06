Summary
-------

The `forgotpwd` cube provides an easy way to generate a new password for an
user, eg the common"I forgot my password" functionnality.

It is non-obstrusive and easy to plug.

Usage
-----

This cube creates a new entity called `Fpasswd`. This is an internal
entity: managers and users can't read/delete or modify this kink of
entity.

The workflow of password recovery is defined below :

1. ask for a new password, the user must have a valid primary email
   associated to his account.

2. An email has been sent. This email contains a generated url associated to an
   user. This link is valid during a short period. This time limit can be
   configured in the all-in-one.conf file:

   .. sourcecode:: ini

      [FORGOTPWD]
      revocation-limit=30 # minutes

3. If the link is valid, the user can change his password in a new form.

There is an automatic task that delete periodically all old Fpasswd which are
stored in the database. This task is started at the launching of the
application.
