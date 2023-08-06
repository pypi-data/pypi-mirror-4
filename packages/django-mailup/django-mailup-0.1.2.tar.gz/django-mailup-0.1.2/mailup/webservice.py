import os
import urllib, urllib2
from mailup import settings
from suds.client import Client
from mailup.utils import xml2obj

#logging.basicConfig(level=logging.INFO)
#logging.getLogger('suds.client').setLevel(logging.DEBUG)
#logging.getLogger('suds.transport').setLevel(logging.DEBUG)

class MailUpSendImport:
    @staticmethod
    def _call(method, **kwargs):
        client = Client(settings.MAILUP_SEND_WS_URL)
        l = client.service.Login(settings.MAILUP_USER, settings.MAILUP_PASSWORD, settings.MAILUP_CONSOLE_URL)
        result = xml2obj(str(l))

        kwargs.update({'accessKey':result.accessKey})
        result = getattr(client.service, method)(**kwargs)

        return xml2obj(str(result))

class MailUpImport:
    @staticmethod
    def _call(method, *params):
        client = Client(settings.MAILUP_IMPORT_WS_URL)

        # Aggiungo l'autenticazione nell'header della richiesta
        token = client.factory.create('Authentication')
        token.User = settings.MAILUP_USER
        token.Password = settings.MAILUP_PASSWORD

        client.set_options(soapheaders=token)

        result = getattr(client.service, method)(*params)
        return xml2obj(str(result))


class MailUpHttp:
    @staticmethod
    def subscribeUser(list_id, list_guid, email, group):
        url = os.path.join(settings.MAILUP_BASE_HTTP_WS_URL, 'xmlSubscribe.aspx')
        values = {
            'ListGuid' : list_guid,
            'list' : list_id,
            'email' : email,
            'group' : group,
            'confirm' : 'false'
        }
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        return response.read().strip()

    @staticmethod
    def unsubscribeUser(list_id, list_guid, email):
        url = os.path.join(settings.MAILUP_BASE_HTTP_WS_URL, 'xmlUnSubscribe.aspx')
        values = {
                    'ListGuid' : list_guid,
                    'List' : list_id,
                    'Email' : email
                 }
        data = urllib.urlencode(values)

        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        return response.read().strip()

    @staticmethod
    def checkSubscriber(list_id, list_guid, email):
        """
        Check if a user is subscribed. Return:
        1 --> Generic error / user not subscribed
        2 --> User subscribed (OPT-IN)
        3 --> User unsubscribed (OPT-OUT)
        4 --> User subscription to be confirmed (PENDING)
        """
        url = os.path.join(settings.MAILUP_BASE_HTTP_WS_URL, 'Xmlchksubscriber.aspx')
        values = {
            'ListGuid' : list_guid,
            'List' : list_id,
            'Email' : email
        }
        data = urllib.urlencode(values)

        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        return response.read().strip()


    @staticmethod
    def updateUser(list_id, list_guid, email, csv_fld_names, csv_fld_values):
        url = os.path.join(settings.MAILUP_BASE_HTTP_WS_URL, 'xmlUpdSubscriber.aspx')
        values = {
                    'ListGuid' : list_guid,
                    'List' : list_id,
                    'Email' : email,
                    'csvFldNames': csv_fld_names,
                    'csvFldValues': csv_fld_values
                 }
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        return response.read().strip()
