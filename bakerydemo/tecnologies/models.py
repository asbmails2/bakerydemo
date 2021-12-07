from django.db import models
from wagtail.snippets.models import register_snippet
from wagtail.admin.edit_handlers import (
    FieldPanel, MultiFieldPanel, StreamFieldPanel
)
from wagtail.core.models import Page
from wagtail.core.fields import StreamField
from bakerydemo.base.blocks import BaseStreamBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@register_snippet
class TecnologyType(models.Model):
    """
    A Django model to define the tecnology type
    It uses the `@register_snippet` decorator to allow it to be accessible
    via the Snippets UI. In the TecnologyPage model you'll see we use a ForeignKey
    to create the relationship between TecnologyType and TecnologyPage. This allows a
    single relationship (e.g only one TecnologyType can be added) that is one-way
    (e.g. TecnologyType will have no way to access related TecnologyPage objects)
    """

    title = models.CharField(max_length=255)

    panels = [
        FieldPanel('title'),
    ]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Tecnology types"

class TecnologyPage(Page):
    """
    Detail view for a specific Tecnology
    """

    introduction = models.TextField(
        help_text = 'Text to describe the page',
        blank = True)
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Tecnology Logo only; horizontal width between 300px and 1000px.'
    )
    body = StreamField(
        BaseStreamBlock(), verbose_name="Page body", blank=True
    )

    tecnology_type= models.ForeignKey(
        'tecnologies.TecnologyType',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    content_panels = Page.content_panels + [
        FieldPanel('introduction', classname="full"),
        ImageChooserPanel('logo'),
        StreamFieldPanel('body'),
        FieldPanel('tecnology_type'),
        
    ]

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    parent_page_types = ['TecnologiesIndexPage']

class TecnologiesIndexPage(Page):
    """
    Index page for Tecnologies
    """
    introduction = models.TextField(
        help_text='Text to describe the page',
        blank=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Landscape mode only; horizontal width between 1000px and '
        '3000px.'
    )
    content_panels = Page.content_panels + [
        FieldPanel('introduction', classname="full"),
        ImageChooserPanel('image'),
    ]

    #can only have TecnologyPage Children
    subpage_types = ['TecnologyPage']

    def get_tecnologies(self):
        return TecnologyPage.objects.live().descendant_of(self).order_by('-first_published_at')
    
    # Allows child objects (e.g. TecnologyPage objects) to be accessible via the
    # template. We use this on the HomePage to display child items of featured
    # content
    def children(self):
        return self.get_children().specific().live()

    def paginate(self, request, *args):
        page = request.GET.get('page')
        paginator = Paginator(self.get_tecnologies(), 12)
        try:
            pages = paginator.page(page)
        except PageNotAnInteger:
            pages = paginator.page(1)
        except EmptyPage:
            pages = paginator.page(paginator.num_pages)
        return pages
    
    def get_context(self, request):
        context = super(TecnologyIndexPage, self).get_context(request)

        #TecnologyPage Objects 

        tecnologies = self.paginate(request, self.get_tecnologies())

        context['tecnologies'] = tecnologies

        return context