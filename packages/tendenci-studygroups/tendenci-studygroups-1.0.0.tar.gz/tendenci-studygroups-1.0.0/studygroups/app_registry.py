from tendenci.core.registry import site
from tendenci.core.registry.base import AppRegistry, lazy_reverse
from studygroups.models import StudyGroup


class StudyGroupRegistry(AppRegistry):
    version = '1.0'
    author = 'Schipul - The Web Marketing Company'
    author_email = 'programmers@schipul.com'
    description = 'Create studygroups type of content'
    
    url = {
        'add': lazy_reverse('studygroups.add'),
        'search': lazy_reverse('studygroups.search'),
    }

site.register(StudyGroup, StudyGroupRegistry)
