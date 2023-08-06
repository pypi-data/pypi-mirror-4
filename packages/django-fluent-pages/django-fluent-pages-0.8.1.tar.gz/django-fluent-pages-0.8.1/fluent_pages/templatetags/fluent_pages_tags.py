"""
Template tags to request fluent page content in the template.
Load this module using:

.. code-block:: html+django

    {% load fluent_pages_tags %}
"""
from django.contrib.sites.models import Site
from django.template import Library
from fluent_pages.models import UrlNode
from fluent_pages.models.navigation import PageNavigationNode
from tag_parser import template_tag
from tag_parser.basetags import BaseInclusionNode, BaseNode

register = Library()


# Please take thread-safety in mind when coding the node classes:
# Only static/unmodified values (like template tag args) should be assigned to self.


@template_tag(register, 'render_breadcrumb')
class BreadcrumbNode(BaseInclusionNode):
    """
    Render the breadcrumb of the site.

    .. code-block:: html+django

        {% render_breadcrumb template="fluent_pages/parts/breadcrumb.html" %}
    """
    tag_name = 'render_breadcrumb'
    template_name = 'fluent_pages/parts/breadcrumb.html'

    def get_context_data(self, parent_context, *tag_args, **tag_kwargs):
        page  = _get_current_page(parent_context)  # CmsObject()
        items = page.breadcrumb # list(CmsObject)

        return {'breadcrumb': items}


@template_tag(register, 'render_menu')
class MenuNode(BaseInclusionNode):
    """
    Render the menu of the site.

    .. code-block:: html+django

        {% render_menu max_depth=1 template="fluent_pages/parts/menu.html" %}
    """
    template_name = 'fluent_pages/parts/menu.html'
    allowed_kwargs = ('max_depth', 'template',)

    def get_context_data(self, parent_context, *tag_args, **tag_kwargs):
        # Get page
        current_page = _get_current_page(parent_context)
        top_pages = UrlNode.objects.toplevel_navigation(current_page=current_page)

        # Construct a PageNavigationNode for every page, that allows simple iteration of the tree.
        # Filter all template tag arguments out that are not supported by the PageNavigationNode.
        node_kwargs = dict((k,v) for k, v in tag_kwargs.iteritems() if k in ('max_depth',))
        return {
            'menu_items': [
                PageNavigationNode(page, current_page=current_page, **node_kwargs) for page in top_pages
            ]
        }


@template_tag(register, 'get_fluent_page_vars')
class GetVarsNode(BaseNode):
    """
    Template Node to setup an application page.

    Introduces the ``site`` and ``page`` variables in the template.
    This can be used for pages that are rendered by a separate application.

    .. code-block:: html+django

        {% get_fluent_page_vars %}
    """
    def render_tag(self, context, *args, **kwargs):
        # If the current URL does not overlay a page,
        # create a dummy item to handle the standard rendering.
        try:
            current_page = _get_current_page(context)
            current_site = current_page.parent_site
        except UrlNode.DoesNotExist:
            # Detect current site
            request = _get_request(context)
            current_page = None
            current_site = Site.objects.get_current()

            # Allow {% render_menu %} to operate.
            dummy_page = UrlNode(title='', in_navigation=False, override_url=request.path, status=UrlNode.DRAFT, parent_site=current_site)
            request._current_fluent_page = dummy_page

        # Automatically add 'site', allows "default:site.domain" to work.
        # ...and optionally - if a page exists - include 'page' too.
        if not context.has_key('site'):
            extra_context = {'site': current_site}
            if current_page and not context.has_key('page'):
                extra_context['page'] = current_page

            context.update(extra_context)

        return ''


# ---- Util functions ----

def _get_current_page(context):
    """
    Fetch the current page.
    """
    request = _get_request(context)

    # This is a load-on-demand attribute, to allow calling the template tags outside the standard view.
    # When the current page is not specified, do auto-detection.
    if not hasattr(request, '_current_fluent_page'):
        try:
            # First start with something you can control,
            # and likely want to mimic from the standard view.
            request._current_fluent_page = context['page']
        except KeyError:
            try:
                # Then try looking up environmental properties.
                request._current_fluent_page = UrlNode.objects.get_for_path(request.path)
            except UrlNode.DoesNotExist, e:
                # Be descriptive. This saves precious developer time.
                raise UrlNode.DoesNotExist("Could not detect current page.\n"
                                           "- " + unicode(e) + "\n"
                                           "- No context variable named 'page' found.")

    return request._current_fluent_page  # is a CmsObject


def _get_request(context):
    """
    Fetch the request from the context.
    This enforces the use of the template :class:`~django.template.RequestContext`,
    and provides meaningful errors if this is omitted.
    """
    assert context.has_key('request'), "The fluent_pages_tags library requires a 'request' object in the context! Is RequestContext not used, or 'django.core.context_processors.request' not included in TEMPLATE_CONTEXT_PROCESSORS?"
    return context['request']

