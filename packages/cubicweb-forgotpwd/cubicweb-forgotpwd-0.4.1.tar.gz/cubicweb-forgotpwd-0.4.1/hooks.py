"""this module contains server side hooks for cleaning forgotpwd table
"""

import random
import string
from datetime import datetime, timedelta

from logilab.common.decorators import monkeypatch
from yams import ValidationError

from cubicweb.selectors import is_instance
from cubicweb.crypto import encrypt
from cubicweb.server import hook
from cubicweb.server.repository import Repository
from cubicweb.sobjects.notification import NotificationView

_ = unicode

class ServerStartupHook(hook.Hook):
    """on startup, register a task to delete old revocation key"""
    __regid__ = 'fpwd_startup'
    events = ('server_startup',)

    def __call__(self):
        # XXX use named args and inner functions to avoid referencing globals
        # which may cause reloading pb
        def cleaning_revocation_key(repo, now=datetime.now):
            session = repo.internal_session()
            try:
                session.execute('DELETE Fpasswd F WHERE F revocation_date < %(date)s',
                                {'date': now()})
                session.commit()
            finally:
                session.close()
        # run looping task often enough to purge pwd-reset requests
        limit = self.repo.vreg.config['revocation-limit'] * 60
        self.repo.looping_task(limit, cleaning_revocation_key, self.repo)


class PasswordResetNotification(NotificationView):
    __regid__ = 'notif_after_add_entity'
    __select__ = is_instance('Fpasswd')

    content = _('''There was recently a request to change the password of your account
on %(base_url)s (login: %(login)s).
If you requested this password change, please set a new password by following
the link below:

%(resetlink)s

If you do not want to change your password, you may ignore this message. The
link expires in %(limit)s minutes.

See you soon on %(base_url)s !
''')

    def subject(self):
        return self._cw._(u'[%s] Request to change your password' % self._cw.base_url())

    def recipients(self):
        fpasswd = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        user = fpasswd.reverse_has_fpasswd[0]
        return [(user.cw_adapt_to('IEmailable').get_email(), user.property_value('ui.language'))]

    def context(self, **kwargs):
        fpasswd = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        link = self._cw.get_shared_data('resetlink', pop=True)
        user = fpasswd.reverse_has_fpasswd[0]
        return {
            'resetlink': link,
            'login': user.login,
            # NOTE: it would probably be better to display the expiration date
            #       (with correct timezone)
            'limit': self._cw.vreg.config['revocation-limit'],
            'base_url': self._cw.base_url(),
            }


@monkeypatch(Repository)
def forgotpwd_send_email(self, data):
    session = self.internal_session()
    revocation_limit = self.config['revocation-limit']
    revocation_id = u''.join([random.choice(string.letters+string.digits)
                              for x in xrange(10)])
    revocation_date = datetime.now() + timedelta(minutes=revocation_limit)
    try:
        existing_requests = session.execute('Any F WHERE U primary_email E, E address %(e)s, U has_fpasswd F',
                                            {'e': data['use_email']})
        if existing_requests:
            raise ValidationError(None, {None: session._('You have already asked for a new password.')})
        rset = session.execute('INSERT Fpasswd X: X revocation_id %(a)s, X revocation_date %(b)s, '
                               'U has_fpasswd X WHERE U primary_email E, E address %(e)s',
                               {'a':revocation_id, 'b':revocation_date, 'e': data['use_email']})
        if not rset:
            raise ValidationError(None, {None: session._(u'An error occured, this email address is unknown.')})
        data['revocation_id'] = revocation_id
        key = encrypt(data, session.vreg.config['forgotpwd-cypher-seed'])
        url = session.build_url('forgottenpasswordrequest',
                                __secure__=True,
                                key=key,)
        session.set_shared_data('resetlink', url)
        # mail is sent on commit
        session.commit()
    finally:
        session.close()


@monkeypatch(Repository)
def forgotpwd_change_passwd(self, data):
    session = self.internal_session()
    try:
        rset = session.execute('Any F, U WHERE U is CWUser, U primary_email E, '
                               'E address %(email)s, EXISTS(U has_fpasswd F, '
                               'F revocation_id %(revid)s)',
                               {'email': data['use_email'],
                                'revid': data['revocation_id']})
        if rset:
            forgotpwd = rset.get_entity(0,0)
            revocation_date = forgotpwd.revocation_date
            user = rset.get_entity(0,1)
            if revocation_date > datetime.now():
                session.execute('SET U upassword %(newpasswd)s WHERE U is CWUser, U eid %(usereid)s',
                                {'newpasswd':data['upassword'].encode('UTF-8'), 'usereid':user.eid})
                session.execute('DELETE Fpasswd F WHERE F eid %(feid)s',
                                {'feid':forgotpwd.eid})
                session.commit()
                msg = session._(u'Your password has been changed.')
            else:
                msg = session._(u'That link has either expired or is not valid.')
        else:
            msg = session._(u'You already changed your password. This link has expired.')
        return msg
    finally:
        session.close()

