# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import TGController
from tg import expose, flash, require, url, lurl, request, redirect, validate, config
from tg.i18n import ugettext as _, lazy_ugettext as l_

try:
    from repoze.what import predicates
except ImportError:
    from tg import predicates

from userprofile.lib import create_user_form, get_user_data, get_profile_css, \
                            update_user_data, create_change_password_form
from tgext.pluggable import app_model, plug_url, primary_key
from tgext.datahelpers.validators import SQLAEntityConverter
from tgext.datahelpers.utils import fail_with

edit_password_form = create_change_password_form()

class RootController(TGController):
    @expose('userprofile.templates.index')
    @validate({'user':SQLAEntityConverter(app_model.User)},
              error_handler=fail_with(404))
    def _default(self, user):
        user_data, user_avatar = get_user_data(user)
        user_displayname = user_data.pop('display_name', (None, 'Unknown'))
        user_partial = config['_pluggable_userprofile_config'].get('user_partial')

        return dict(user=user, is_my_own_profile=request.identity and request.identity['user'] == user,
                    user_data=user_data, user_avatar=user_avatar,
                    user_displayname=user_displayname,
                    profile_css=get_profile_css(config),
                    user_partial=user_partial)

    @expose('userprofile.templates.edit')
    @require(predicates.not_anonymous())
    def edit(self):
        user = request.identity['user']
        user_data, user_avatar = get_user_data(user)
        user_data = dict([(fieldid, info[1]) for fieldid, info in user_data.items()])
        return dict(user=user_data, profile_css=get_profile_css(config),
                    user_avatar=user_avatar,
                    form=create_user_form(user))

    @expose()
    @require(predicates.not_anonymous())
    def save(self, **kw):
        user = request.identity['user']
        profile_save = getattr(user, 'save_profile', None)
        if not profile_save:
            profile_save = update_user_data
        profile_save(user, kw)
        flash(_('Profile successfully updated'))
        return redirect(plug_url('userprofile', '/%s' % getattr(user, primary_key(app_model.User).name)))

    @expose('userprofile.templates.chpasswd')
    @require(predicates.not_anonymous())
    def chpasswd(self, **kw):
        return dict(profile_css=get_profile_css(config),
                    form=edit_password_form)

    @require(predicates.not_anonymous())
    @expose()
    @validate(edit_password_form, error_handler=chpasswd)
    def save_password(self, password, verify_password):
        user = request.identity['user']
        user.password = password
        flash(_('Password successfully changed'))
        return redirect(plug_url('userprofile', '/%s' % getattr(user, primary_key(app_model.User).name)))

    @require(predicates.not_anonymous())
    @expose('userprofile.templates.index')
    def me(self):
        user=request.identity['user']
        return redirect(plug_url('userprofile', '/%s' % getattr(user, primary_key(app_model.User).name)))