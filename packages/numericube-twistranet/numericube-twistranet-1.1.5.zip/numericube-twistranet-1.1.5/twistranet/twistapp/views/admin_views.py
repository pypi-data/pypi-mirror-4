from django.utils.translation import ugettext as _
from django.http import HttpResponse
from django.template import loader, Context
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.contrib import messages
from twistranet.core.views import BaseView, BaseIndividualView
from twistranet.twistapp.views.account_views import HomepageView
from twistranet.twistapp.forms.admin_forms import *
from twistranet.twistapp.models import Twistable, Menu, MenuItem, Community, GlobalCommunity
from twistranet.actions import *

try:
    #python >= 2.6
    import json
except:
    #python 2.5
    import simplejson as json

label_save = _('Save')
label_edit_menuitem = _('Edit menu entry')
label_delete_menuitem = _('Delete menu entry')
label_cancel = _('Cancel')

def get_item_template(id, label, title, description, parent_id, target_id,
                      link_url, view_path, type, position, level=0,
                      edit_form = None, state='inactive', status='edit'):

    t = loader.get_template('admin/menu_item_edit.part.html')
    c = Context ({'iid': id,
                 'ilabel': label,
                 'ititle': title,
                 'idescription': description,
                 'iparent_id': parent_id,
                 'itarget_id': target_id,
                 'ilink_url': link_url,
                 'iview_path': view_path,
                 'itype': type,
                 'iposition': position,
                 'level': level,
                 'label_edit_menuitem': label_edit_menuitem,
                 'label_save': label_save,
                 'label_delete_menuitem': label_delete_menuitem,
                 'label_cancel': label_cancel,
                 'edit_form' : edit_form,
                 'state': state,
                 'status': status,
                })
    return t.render(c)

def get_item_model(menu):
    """html model used by javascript
       to generate new item edit forms
       the prefix 'model-' is used by javascript to change values
    """
    return get_item_template('model-id', 'model-label', 'model-title', 'model-description', menu.id, 'model-target_id',
                             'model-link_url', 'model-view_path', 'model-type', 'model-position', level=0,
                              edit_form = None, state='active', status='add')

# used for menu_builder html calls
def get_html_menu_tree( menu, level=-1):
    html = ''
    level += 1
    position = 0
    for menuitem in menu.children:
        position += 1
        if menuitem.target:
            type = 'content'
            target_id = menuitem.target.object.id
            link_url = ''
            view_path = ''
            edit_form = MenuItemContentForm(instance=menuitem, initial={'target_id': target_id})
        elif menuitem.link_url:
            type = 'link'
            target_id = ''
            link_url = menuitem.link_url
            view_path = ''
            edit_form = MenuItemLinkForm(instance=menuitem)
        elif menuitem.view_path:
            type = 'view'
            target_id = ''
            link_url = ''
            view_path = menuitem.view_path
            edit_form = MenuItemViewForm(instance=menuitem)
        else:
            raise("Something's strange with this menuitem")
        html += get_item_template(menuitem.id, menuitem.label, menuitem.title, menuitem.description,
                                  menu.id, target_id, link_url, view_path, type, position, level, edit_form, 'inactive', 'edit')
        html += get_html_menu_tree(menuitem, level)
    return html

class MenuBuilder(BaseView):
    """
    A view used to build all menus
    """
    name = "menu_builder"
    template_variables = BaseView.template_variables + [
        "form",
        "menu",
        "topmenus",
        "mainmenu",
        "links_form",
        "view_form",
        "content_form",
        "referer_url",
        "item_model",
        "communities",
    ]
    template = 'admin/menu_builder_form.html'
    title = _("Menu Builder")
    category = GLOBAL_ACTIONS

    def as_action(self,):
        """
        Check that I'm an admin
        """
        if GlobalCommunity.objects.exists():
            glob = GlobalCommunity.get()
            if glob.can_edit:
                return BaseView.as_action(self,)

    def prepare_view(self, *args, **kw):

        if self.request.method == 'POST':
            req = self.request.POST
            menuitems = {}
            menuID = req.get('menu-id')
            for key in req.keys():
                k_split =  key.split('-')
                if len(k_split)>1 and key!='menu-id':
                    itemID = k_split[-1]
                    itemkey =k_split[-2]
                    if not menuitems.has_key(itemID):
                        menuitems[itemID] = {}
                    menuitems[itemID][itemkey] = req.get(key)

            # TODO XXX JMG : order by status/ and by id, so we will be able to edit everything in one pass only
            # just change status before with  1= add, 2 = edit, 3 = delete
            # first pass create all new items
            for id in menuitems.keys():
                status  = menuitems[id][u'status']
                if status==u'add':
                    newitem = MenuItem.objects.create(
                        parent_id = menuID,
                        title =  menuitems[id][u'title'],
                        link_url = 'tempValueForModelValidation'
                    )
                    menuitems[id][u'realId'] = newitem.id
                    menuitems[id][u'status'] = 'edit'
            # second pass edit all items
            for id in menuitems.keys():
                status  = menuitems[id][u'status']
                if status==u'edit':
                    if menuitems[id].has_key(u'realId') :
                        item = MenuItem.objects.get(id = menuitems[id][u'realId'])
                    else:
                        item = MenuItem.objects.get(id = id)
                    parent_id = menuitems[id][u'parent_id']
                    # the case when parent was a temp item just added
                    if parent_id.startswith(u'tempID'):
                        parent_id = menuitems[parent_id][u'realId']
                    item.parent = MenuItem.objects.get(id = parent_id)
                    target_id = menuitems[id][u'target_id']
                    if target_id:
                        item.target = Twistable.objects.get(id = target_id)
                    for k in (u'title', u'description', u'link_url', u'view_path'):
                         setattr(item, k, menuitems[id][k])
                    item.order = int(menuitems[id][u'position'])
                    item.save()

            # last pass delete
            for id in menuitems.keys():
                status  = menuitems[id][u'status']
                if status==u'delete':
                    item = MenuItem.objects.get(id = id)
                    item.delete()

            # and finally save root menu to apply the model order rules
            menu = Menu.objects.get(id = menuID)
            menu.save()
            messages.info(self.request, _("Menu has been saved."))

        self.account = self.auth
        self.topmenus = topmenus = Menu.objects.all()
        # start the menu builder for the first menu if exists
        if topmenus:
            self.menu = topmenus[0]
            self.mainmenu = '<ul id="menu-to-edit" class="menu ui-sortable">\n%s\n</ul>' %get_html_menu_tree(self.menu)
            self.item_model = get_item_model(self.menu)
            self.title = '%s : %s' %(self.title, self.menu.title)
        else:
            self.menu = None
            self.mainmenu = ''
            self.item_model = ''
        self.form = MenuBuilderForm()
        self.links_form = MenuItemLinkForm()
        self.view_form = MenuItemViewForm()
        self.content_form = MenuItemContentForm()
        referer_path = reverse(HomepageView.name)
        self.referer_url = self.request.build_absolute_uri(referer_path)
        self.communities = Community.objects.get_query_set()[:10]


class MenuItemValidate(BaseView):
    """
    This view return inline validation in json format
    for menuitem inline forms, or just for a field
    """
    title = "Menu Item - Validation"
    name = "menuitem_validate"
    itemtype = ""
    form_class = MenuItemForm
    fieldname = 'all'

    def prepare_view(self, itemtype, fieldname):
        if itemtype == 'link':
            self.form_class = MenuItemLinkForm
        elif itemtype == 'content':
            self.form_class = MenuItemContentForm
        elif itemtype == 'view':
            self.form_class = MenuItemViewForm
        else:
            raise NotImplementedError("this menu item type doesn't exist")

        self.fieldname = fieldname

        self.form = self.form_class(self.request.POST)

    def render_view(self,):
        if self.request.method == 'POST':
            fieldname = self.fieldname
            # unik field validation
            if fieldname != 'all':
                form = self.form
                value = form.data[fieldname]
                f = form.fields[fieldname]
                try:
                    f.validate(value)
                    f.run_validators(value)
                    success = True
                    errors = {}
                except ValidationError, e:
                    success = False
                    errors = {fieldname : e.messages}
                data =  {'success' : success, 'errors' : errors}
            # entire form validation
            else :
                data =  {'success' : self.form.is_valid(), 'errors' : self.form.errors}
            return HttpResponse( json.dumps(data),
                                 mimetype='text/plain')
