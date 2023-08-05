from django.utils.translation import ugettext as _
from django import forms
from django.forms import widgets
from django.forms import fields
from twistranet.twistapp.forms.base_forms import BaseForm
from twistranet.twistapp.forms.fields import ViewPathField, LargeURLField
from twistranet.twistapp.models import Menu, MenuItem


class MenuBuilderForm(forms.Form):
    """just a basic form to build menus
    """

class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ('title', 'description', )

class MenuItemForm(forms.ModelForm):

    title = fields.CharField(
        required = True,
        label = _("Title"),
        help_text = _("Enter the item's title as you want it to be displayed in menu."),
        widget = widgets.TextInput(attrs = {'id': ''}),
    )

    description = fields.CharField(
        label = _("Description"),
        required = False,
        help_text = _("Enter the item's description as you want it to be displayed on mouse over menu item's."),
        widget = widgets.Textarea(attrs = {'class': 'menu-description-field', 'rows':'2', 'cols': '', 'id': ''}),
    )

    class Meta:
        model = MenuItem
        fields = ('title', 'description' )

class MenuItemLinkForm(MenuItemForm):

    link_url = LargeURLField(
        label = "URL",
        help_text = _("Enter a custom link's url. It could be an external or internal valid url."),
        required = True,
        initial='http://',
        widget = widgets.TextInput(attrs = {'id': ''}),
        )
    class Meta:
        model = MenuItem
        fields = ('title', 'description', 'link_url')

class MenuItemContentForm(MenuItemForm):
    """the edit form for a target (community or anything else)"""
    title = fields.CharField(
        required = False,
        label = _("Title"),
        help_text = _("Enter the item's title as you want it to be displayed in menu. Leave it blank if you want to keep the target title."),
        widget = widgets.TextInput(attrs = {'id': ''}),
    )

    description = fields.CharField(
        label = _("Description"),
        required = False,
        help_text = _("Enter the item's description as you want it to be displayed on mouse over menu item's. Leave it blank if you want to keep the target description."),
        widget = widgets.Textarea(attrs = {'class': 'menu-description-field', 'rows':'2', 'cols': '', 'id': ''}),
    )

    target_id = forms.IntegerField(required = True, widget = widgets.HiddenInput)

    class Meta:
        model = MenuItem
        fields = ('title', 'description', 'target_id' )

class MenuItemViewForm(MenuItemForm):

    view_path = ViewPathField(
        label = "View Path",
        help_text = _("Enter the internal view path."),
        required = True,
        widget = widgets.TextInput(attrs = {'id': ''}),
        )
    class Meta:
        model = MenuItem
        fields = ('title', 'description', 'view_path')