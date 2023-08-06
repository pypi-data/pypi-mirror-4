from haystack import indexes
from haystack import site

from tendenci.core.perms.indexes import TendenciBaseSearchIndex
from tendenci.core.categories.models import Category
from committees.models import Committee

class CommitteeIndex(TendenciBaseSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title',)

    # categories
    category = indexes.CharField()
    sub_category = indexes.CharField()

    # RSS fields
    can_syndicate = indexes.BooleanField()
    order = indexes.DateTimeField()

    def prepare_category(self, obj):
        category = Category.objects.get_for_object(obj, 'category')
        if category:
            return category.name
        return ''

    def prepare_sub_category(self, obj):
        category = Category.objects.get_for_object(obj, 'sub_category')
        if category:
            return category.name
        return ''

    def prepare_can_syndicate(self, obj):
        return obj.allow_anonymous_view and obj.status == 1 \
        and obj.status_detail == 'active'

    def prepare_syndicate_order(self, obj):
        return obj.update_dt

site.register(Committee, CommitteeIndex)
