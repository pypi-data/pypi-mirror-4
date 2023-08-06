from tendenci.core.registry import site
from tendenci.core.registry.base import AppRegistry, lazy_reverse
from committees.models import Committee


class CommitteeRegistry(AppRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create committees type of content'
    
    url = {
        'add': lazy_reverse('committees.add'),
        'search': lazy_reverse('committees.search'),
    }

site.register(Committee, CommitteeRegistry)
