# -*- coding: utf-8 -*-
""" Live Contact Importer module """

from .base import BaseProvider
from urllib import urlencode
import requests
import json

AUTH_URL = "https://login.live.com/oauth20_authorize.srf"
TOKEN_URL = "https://login.live.com/oauth20_token.srf"
PERM_SCOPE = "wl.basic,wl.contacts_emails"
CONTACTS_URL = "https://apis.live.net/v5.0/me/contacts?access_token=%s&limit=1000"


class LiveContactImporter(BaseProvider):

    def __init__(self, *args, **kwargs):
        super(LiveContactImporter, self).__init__(*args, **kwargs)
        self.auth_url = AUTH_URL
        self.token_url = TOKEN_URL
        self.perm_scope = PERM_SCOPE

    def request_authorization(self):
        auth_params = {
            "response_type": "code",
            "scope": PERM_SCOPE,
            "redirect_uri": self.redirect_url,
            "client_id": self.client_id
        }

        return "%s?%s" % (self.auth_url, urlencode(auth_params))

    def request_access_token(self, code):
        access_token_params = {
            "code" : code,
            "client_id" : self.client_id,
            "client_secret" : self.client_secret,
            "redirect_uri" : self.redirect_url,
            "grant_type": "authorization_code",
        }

        content_length = len(urlencode(access_token_params))
        access_token_params['content-length'] = str(content_length)

        response = requests.post(self.token_url, data=access_token_params)
        data = json.loads(response.text)
        return data.get('access_token')

    def import_contacts(self, access_token):
        authorization_header = {
            "Authorization": "OAuth %s" % access_token,
            "GData-Version": "3.0"
        }
        response = requests.get(CONTACTS_URL % access_token)
        return self.parse_contacts(response.text)

    def parse_contacts(self, contacts_json):
        contacts_list = json.loads(contacts_json)
        contacts = []
        for contact in contacts_list['data']:
            emails = contact['emails']
            if emails.get('account'):
                contacts.append(emails['account'])
        return contacts


