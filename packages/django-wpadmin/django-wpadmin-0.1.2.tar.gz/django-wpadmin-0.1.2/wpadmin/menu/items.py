from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _


from wpadmin.menu.utils import UserTestElementMixin, AppListElementMixin


class MenuItem(UserTestElementMixin):
    """
    This is the base class for custom menu items.
    A menu item can have the following properties:

    ``title``
        String that contains the menu item title, make sure you use the
        django gettext functions if your application is multilingual.
        Default value: 'Untitled menu item'.

    ``url``
        String that contains the menu item URL.
        Default value: None (will be rendered as 'javascript:;').

    ``add_url``
        An optional string that contains second menu item URL. This url allows
        to have edit and add urls in one menu item. add_url is small plus sign
        in menu, next to normal url.
        Default value: None.

    ``icon``
        An optional string which contains name of icon from Font Awesome which
        should be used for this menu item. Note that icons may not show on all
        levels of menu.
        Default value: None.

    ``css_classes``
        A list of css classes to be added to the menu item class attribute.
        Default value: [].

    ``description``
        An optional string that will be used as the ``title`` attribute of
        the menu-item ``a`` tag.
        Default value: None.

    ``enabled``
        Boolean that determines whether the menu item is enabled or not.
        Disabled items are displayed but are not clickable.
        Default value: True.

    ``template``
        The template to use to render the menu item.
        Default value: 'admin_tools/menu/item.html'.

    ``children``
        A list of children menu items. All children items must be instances of
        the ``MenuItem`` class.
    """

    title = 'Untitled menu item'
    url = None
    add_url = None
    icon = None
    css_classes = None
    description = None
    enabled = True
    template = 'wpadmin/menu/item.html'
    children = None

    def __init__(self, title=None, url=None, **kwargs):

        if title is not None:
            self.title = title

        if url is not None:
            self.url = url

        for key in kwargs:
            if hasattr(self.__class__, key):
                setattr(self, key, kwargs[key])
        self.children = self.children or []
        self.css_classes = self.css_classes or []

    def init_with_context(self, context):
        """
        """
        pass

    def is_selected(self, request):
        """
        Helper method that returns ``True`` if the menu item is active.
        A menu item is considered as active if it's url or add_url or one of its
        descendants url or add_url is equals to the current URL.
        """
        current_url = request.path
        #TODO: also check edit urls (with number at the end)
        return self.url == current_url or \
            self.add_url == current_url or \
            len([c for c in self.children if c.is_selected(request)]) > 0

    def is_empty(self):
        """
        Helper method that returns ``True`` if the menu item is empty.
        This method always returns ``False`` for basic items, but can return
        ``True`` if the item is an AppList.
        """
        return False


class AppList(AppListElementMixin, MenuItem):

    def __init__(self, title=None, models=None, exclude=None, **kwargs):
        self.models = list(models or [])
        self.exclude = list(exclude or [])
        super(AppList, self).__init__(title, **kwargs)

    def init_with_context(self, context):

        items = self._visible_models(context)
        apps = {}
        for model, perms in items:
            if not perms['change']:
                continue
            app_label = model._meta.app_label
            if app_label not in apps:
                apps[app_label] = {
                    'title': capfirst(_(app_label.title())),
                    'url': self._get_admin_app_list_url(model, context),
                    'models': []
                }
            apps[app_label]['models'].append({
                'title': capfirst(model._meta.verbose_name_plural),
                'url': self._get_admin_change_url(model, context),
                'add_url': self._get_admin_add_url(model, context),
                'description': _(u"Change"),
            })

        apps_sorted = apps.keys()
        apps_sorted.sort()
        for app in apps_sorted:
            app_dict = apps[app]
            item = MenuItem(title=app_dict['title'], url=app_dict['url'],
                            description=app_dict['title'])
            # sort model list alphabetically
            apps[app]['models'].sort(lambda x, y: cmp(x['title'], y['title']))
            for model_dict in apps[app]['models']:
                model_item = MenuItem(**model_dict)
                model_item.add_url = model_dict['add_url']
                item.children.append(model_item)
            self.children.append(item)


class ModelList(AppListElementMixin, MenuItem):

    def __init__(self, title=None, models=None, exclude=None, **kwargs):
        self.models = list(models or [])
        self.exclude = list(exclude or [])

        super(ModelList, self).__init__(title, **kwargs)

    def init_with_context(self, context):

        items = self._visible_models(context)
        for model, perms in items:
            if not perms['change']:
                continue
            title = capfirst(model._meta.verbose_name_plural)
            url = self._get_admin_change_url(model, context)
            add_url = self._get_admin_add_url(model, context)
            item = MenuItem(title=title, url=url, description=title)
            item.add_url = add_url
            self.children.append(item)


class UserTools(MenuItem):

    is_user_tools = True
    css_classes = ['float-right']


# class Bookmarks(MenuItem, AppListElementMixin):
#
#    title = _('Bookmarks')
#    icon = 'icon-bookmark'
#    css_classes = ['float-right', 'bookmarks']
#    is_bookmarks = True
#
#    def init_with_context(self, context):
#
#        from admin_tools.menu.models import Bookmark
#
#        for b in Bookmark.objects.filter(user=context['request'].user):
#            self.children.append(MenuItem(mark_safe(b.title), b.url, is_bookmark=True))


