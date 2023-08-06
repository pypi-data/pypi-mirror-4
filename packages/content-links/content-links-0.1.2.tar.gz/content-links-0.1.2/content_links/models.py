from django.db import models
from django.forms import ValidationError
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from feincms import settings
from feincms.admin.item_editor import ItemEditorForm
from feincms.content.section.models import SectionContent, SectionContentInline


class ContentLinkItemEditorForm(ItemEditorForm):
    def clean_mediafile(self):
        mediafile = self.cleaned_data.get('mediafile', None)
        if mediafile and not mediafile.type == 'image':
            raise ValidationError('Please select only image file.')
        return mediafile

    def clean(self):
        cleaned_data = self.cleaned_data
        target = self.cleaned_data.get('target', None)
        target_url = self.cleaned_data.get('target_url', None)
        if target and target_url:
            raise ValidationError('''Please specify either "Target page" OR
                "Target URL". Not both.''')
        return cleaned_data


class ContentLinkAdminInline(SectionContentInline):
    form = ContentLinkItemEditorForm
    raw_id_fields = ('mediafile', 'target')


class ContentLink(SectionContent):
    """
    Content links allow you to link other page(s) or URLs to specific page.

    Create a content links as follow:

        Page.create_content_type(ContentLink, TYPE_CHOICES=(
            ('one', _('One')),
            ('two', _('Two')),
            ('three', _('And three')),
        )

    """
    feincms_item_editor_includes = {
        'head': [
            settings.FEINCMS_RICHTEXT_INIT_TEMPLATE,
            'admin/content/content_links/init.html',
        ],
    }
    target = models.ForeignKey('page.Page', blank=True, null=True,
        verbose_name=_('Target page'),
        related_name='%(app_label)s_%(class)s_related',
        help_text=_('''Page to be linked to. Do not add both "Target page" and
            "Target URL".''')
    )

    target_url = models.URLField(blank=True, null=True,
        verbose_name=_('Target URL'),
        help_text=_('''URL to link to. Do not add both "Target page" and
            "Target URL".''')
    )

    class Meta:
        abstract = True
        verbose_name = _('content link')
        verbose_name_plural = _('content links')

    @property
    def url(self):
        if self.target:
            return self.target.get_absolute_url()
        return self.target_url

    @classmethod
    def initialize_type(cls, TYPE_CHOICES=None, cleanse=False):
        super(ContentLink, cls).initialize_type(TYPE_CHOICES, cleanse)

        # use custom form in order to perform validation on target fields
        cls.feincms_item_editor_inline = ContentLinkAdminInline

    def render(self, **kwargs):
        return render_to_string([
            'content/content_links/%s/%s.html' % (self.region, self.type),
            'content/content_links/%s/default.html' % self.region,
            'content/content_links/%s.html' % self.type,
            'content/content_links/default.html',
        ], {'content': self})
