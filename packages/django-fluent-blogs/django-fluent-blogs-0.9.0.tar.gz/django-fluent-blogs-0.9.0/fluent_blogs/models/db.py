from django.conf import settings
from django.db.models import get_model
from django.utils.translation import ugettext_lazy as _
from fluent_blogs.base_models import AbstractEntry, CommentsEntryMixin
from fluent_blogs import appsettings


class Entry(AbstractEntry):
    """
    The actual blog entry
    """
    class Meta:
        app_label = 'fluent_blogs'  # required for models subfolder
        verbose_name = _("Blog entry")
        verbose_name_plural = _("Blog entries")


_EntryModel = None

def get_entry_model():
    """
    Return the actual entry model that is in use.
    """
    global _EntryModel
    if not appsettings.FLUENT_BLOGS_ENTRY_MODEL:
        return Entry

    if _EntryModel is None:
        app_label, model_name = appsettings.FLUENT_BLOGS_ENTRY_MODEL.rsplit('.', 1)
        _EntryModel = get_model(app_label, model_name)

        # Auto-register with django-fluent-comments moderation
        if 'fluent_comments' in settings.INSTALLED_APPS and isinstance(_EntryModel, CommentsEntryMixin):
            from fluent_comments.moderation import moderate_model
            moderate_model(_EntryModel,
                publication_date_field='publication_date',
                enable_comments_field='enable_comments',
            )

        # Auto-register with django-any-urlfield
        if 'any_urlfield' in settings.INSTALLED_APPS:
            from any_urlfield.models import AnyUrlField
            from any_urlfield.forms.widgets import SimpleRawIdWidget
            AnyUrlField.register_model(_EntryModel, widget=SimpleRawIdWidget(_EntryModel))

    return _EntryModel


def get_category_model():
    """
    Return the category model to use.
    """
    app_label, model_name = appsettings.FLUENT_BLOGS_CATEGORY_MODEL.rsplit('.', 1)
    return get_model(app_label, model_name)
