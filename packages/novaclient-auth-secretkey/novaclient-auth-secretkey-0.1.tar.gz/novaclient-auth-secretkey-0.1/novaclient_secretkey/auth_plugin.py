"""
Authentication plugin for python-novaclient.  Enables using API key+secret key
credentials instead of username+password.
"""
import os


def secretkey(httpclient, url):
    # Prefer the credentials hanging off the httpclient object, and fall back
    # to picking them out of the environment.  This allows convenient access
    # for both API consumers and CLI tool users.
    key_id = getattr(
            httpclient,
            'os_access_key_id',
            os.environ.get('OS_ACCESS_KEY_ID', 'NO KEY ID'),
            )
    secret_key = getattr(
            httpclient,
            'os_secret_key',
            os.environ.get('OS_SECRET_KEY', 'NO SECRET KEY'),
            )
    body = {
            "auth": {
                "apiAccessKeyCredentials": {
                    "accessKey": key_id,
                    "secretKey": secret_key,
                    }
                }
            }
    if httpclient.projectid:
        body['auth']['tenantName'] = httpclient.projectid
    httpclient._authenticate(url, body)
