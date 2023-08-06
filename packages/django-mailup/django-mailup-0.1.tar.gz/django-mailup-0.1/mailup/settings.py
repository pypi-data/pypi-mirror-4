import os
from django.conf import settings

MAILUP_CONSOLE_URL = getattr(settings, 'MAILUP_CONSOLE_URL', '') # Mailup base console url : eg: http://mailup.dominio.it
MAILUP_USER = getattr(settings, 'MAILUP_USER', '')
MAILUP_PASSWORD = getattr(settings, 'MAILUP_PASSWORD', '')

MAILUP_SEND_WS_URL = getattr(settings, 'MAILUP_SEND_WS_URL', 'https://wsvc.ss.mailup.it/MailupSend.asmx?WSDL')
MAILUP_IMPORT_WS_URL = getattr(settings, 'MAILUP_IMPORT_WS_URL', os.path.join(MAILUP_CONSOLE_URL, '/services/WSMailUpImport.asmx?WSDL'))
MAILUP_BASE_HTTP_WS_URL = getattr(settings, 'MAILUP_BASE_HTTP_WS_URL', os.path.join(MAILUP_CONSOLE_URL, 'frontend'))

MAILUP_TEST_GUID = getattr(settings, 'MAILUP_TEST_GUID', '')
MAILUP_TEST_ID_LIST = getattr(settings, 'MAILUP_TEST_ID_LIST', '')
MAILUP_TEST_ID_GROUP = getattr(settings, 'MAILUP_TEST_ID_GROUP', '')
MAILUP_TEST_EMAIL = getattr(settings, 'MAILUP_TEST_EMAIL', '')