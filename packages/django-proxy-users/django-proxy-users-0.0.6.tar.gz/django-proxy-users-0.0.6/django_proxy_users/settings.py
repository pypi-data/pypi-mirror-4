from django.conf import settings

SESSION_ORIGINAL_USER_KEY = getattr(settings, 'SESSION_ORIGINAL_USER_KEY', '_ORIGINAL_USER_KEY')
TEMPLATE_ORIGINAL_USER_KEY = getattr(settings, 'TEMPLATE_ORIGINAL_USER_KEY', 'original_user')
RECORDS_PER_PAGE = getattr(settings, 'RECORDS_PER_PAGE', 100)
