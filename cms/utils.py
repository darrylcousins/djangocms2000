from django.utils.text import Truncator
from django.utils.functional import allow_lazy

def truncate_words(s, num, end_text='...'):
    truncate = end_text and ' %s' % end_text or ''
    return Truncator(s).words(num, truncate=truncate)
truncate_words = allow_lazy(truncate_words, unicode)

# test the request object to see if we're in edit mode
def is_editing(request):
    return ('cms-edit_mode' in request.COOKIES) and request.user.has_module_perms("cms")
