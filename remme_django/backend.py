import json
import requests
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from hashlib import sha256
from django.conf import settings

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User

class AuthenticationBackend(object):
    def authenticate(self, request):
        def jsonrpc_request(method, *args, **kwargs):
            request_data = {
                'jsonrpc': '2.0',
                'id': 0,
                'method': method
            }
            if args:
                request_data['params'] = args
            elif kwargs:
                request_data['params'] = kwargs
            request = requests.post(settings.REMME['BITCOIN_API']['URL'],
                                    auth=(settings.REMME['BITCOIN_API']['USER'],
                                          settings.REMME['BITCOIN_API']['PASSWORD']),
                                    data=json.dumps(request_data))
            return request.json()

        if request.META.get('HTTP_X_SSL_AUTHENTICATED') == 'NONE':
            return None

        dn = request.META.get('HTTP_X_SSL_USER_DN')
        user_data = dict(i.split('=', 1) for i in dn.split(',') if i != '')
        revoked = (jsonrpc_request('gettxout',
                                   user_data['OU'],
                                   int(user_data['ST']))['result'] == None)
        if revoked:
            return None
        
        certificate_raw = request.META.get('HTTP_X_SSL_CERTIFICATE')
        certificate = x509.load_pem_x509_certificate(certificate_raw.encode(), default_backend())
        public_key = certificate.public_key().public_bytes(serialization.Encoding.DER,
                                                           serialization.PublicFormat.PKCS1)
        public_key_hash = sha256()
        public_key_hash.update(public_key)
        public_key_hash_hex = public_key_hash.hexdigest()
        user_data['L'] = user_data['L'].replace('\\', '')
        verification_message = 'http://remme.io/certificate/{}/{}/{}/{}'.format(
            certificate.serial_number,
            public_key_hash_hex,
            user_data['OU'],
            user_data['ST'])
        verified = jsonrpc_request('verifymessage',
                                   user_data['UID'],
                                   user_data['L'],
                                   verification_message)['result']
        if not verified:
            return None

        try:
            user = User.objects.get(username=user_data['UID'])
        except User.DoesNotExist:
            if settings.REMME['AUTOCREATE_VALID_USERS']:
                user = User(username=user_data['UID'])
                user.save()
            else:
                return None
        return user
        
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
