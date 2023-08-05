import copy
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.utils.translation import ugettext_lazy as _
from fluent_pages.admin.urlnodeadmin import UrlNodeAdmin, UrlNodeAdminForm
from fluent_pages.models import Page, HtmlPage


class PageAdminForm(UrlNodeAdminForm):
    pass


class PageAdmin(UrlNodeAdmin):
    """
    The base class for pages
    """
    base_model = Page
    base_form = PageAdminForm

    class Media:
        js = ('fluent_pages/admin/django13_fk_raw_id_fix.js',)


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super(PageAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if field is None:
            return None

        # Hack the ForeignKeyRawIdWidget in Django 1.4 to display a selector for the base model too.
        # It correctly detects that the parent field actually points to an UrlNode, instead of Page.
        # Since UrlNode is not registered in the admin, it won't display the selector. Overriding that here.
        # It also partially fixes Django 1.3, which would wrongly point the url to ../../../fluent_pages/urlnode/ otherwise.
        if db_field.name == 'parent' and isinstance(field.widget, ForeignKeyRawIdWidget):
            field.widget.rel = copy.copy(field.widget.rel)
            field.widget.rel.to = Page

        return field



class HtmlPageAdmin(PageAdmin):
    """
    The modeladmin configured to display :class:`~fluent_pages.models.HtmlPage` objects.
    """
    FIELDSET_SEO = (_('SEO settings'), {
        'fields': ('keywords', 'description'),
        'classes': ('collapse',),
    })

    base_fieldsets = (
        PageAdmin.FIELDSET_GENERAL,
        FIELDSET_SEO,
        PageAdmin.FIELDSET_MENU,
        PageAdmin.FIELDSET_PUBLICATION,
    )
