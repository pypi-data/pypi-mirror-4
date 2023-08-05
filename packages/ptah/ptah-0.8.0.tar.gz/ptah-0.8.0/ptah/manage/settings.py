""" settings module """
import pform
import ptah
from ptah.settings import ID_SETTINGS_GROUP
from pyramid.decorator import reify
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound


@ptah.manage.module('settings')
class SettingsModule(ptah.manage.PtahModule):
    __doc__ = 'The current settings which include defaults not used by .ini'

    title = 'Settings'

    def __getitem__(self, key):
        grp = ptah.get_settings(key, self.request.registry)
        if grp is not None and grp.__ttw__:
            return SettingsWrapper(grp, self)
        raise KeyError(key)


class SettingsWrapper(object):

    def __init__(self, grp, mod):
        self.__name__ = grp.__name__
        self.__parent__ = mod
        self.group = grp


@view_config(
    context=SettingsModule, wrapper=ptah.wrap_layout(),
    renderer='ptah-manage:settings.lt')

class SettingsView(ptah.View):
    """ Settings manage module view """

    grps = None

    def update(self):
        groups = ptah.get_cfg_storage(ID_SETTINGS_GROUP).items()

        data = []
        for name, group in sorted(groups):
            if self.grps is not None and name not in self.grps:
                continue

            title = group.__title__ or name
            description = group.__description__

            schema = []
            for field in group.__fields__.values():
                if getattr(field, 'tint', False):
                    value = '* * * * * * *'
                else:
                    value = ptah.json.dumps(group[field.name])
                schema.append(
                    ({'name': '{0}.{1}'.format(name, field.name),
                      'type': field.__class__.__name__,
                      'value': value,
                      'title': field.title,
                      'description': field.description,
                      'default': ptah.json.dumps(field.default)}))

            data.append(
                ({'title': title,
                  'description': description,
                  'schema': schema,
                  'name': group.__name__,
                  'ttw': group.__ttw__}))

        return {'data': sorted(data, key=lambda item: item['title'])}


@view_config(context=SettingsWrapper, wrapper=ptah.wrap_layout())
class EditForm(pform.Form):
    """ Settings group edit form """

    @reify
    def label(self):
        return self.context.group.__title__

    @reify
    def description(self):
        return self.context.group.__description__

    @reify
    def fields(self):
        grp = self.context.group
        return grp.__fields__.omit(*grp.__ttw_skip_fields__)

    def form_content(self):
        return self.context.group

    @pform.button('Modify', actype=pform.AC_PRIMARY)
    def modify_handler(self):
        data, errors = self.extract()
        if errors: # pragma: no cover
            self.add_error_message(errors)
            return

        self.request.add_message("Settings have been modified.")
        self.context.group.updatedb(**data)
        return HTTPFound('../#{0}'.format(self.context.group.__name__))

    #@pform.button('Reset defaults', actype=pform.AC_INFO)
    #def reset_handler(self):
    #    pass

    @pform.button('Back')
    def back_handler(self):
        return HTTPFound('..')
