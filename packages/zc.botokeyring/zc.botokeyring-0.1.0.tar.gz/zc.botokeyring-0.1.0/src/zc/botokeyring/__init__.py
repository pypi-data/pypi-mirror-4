import boto
import keyring

def setup():
    kr = boto.config.get('Credentials', 'keyring')
    if kr:
        pw = keyring.get_password(
            kr, boto.config.get('Credentials', 'aws_access_key_id'))
        boto.config.set('Credentials', 'aws_secret_access_key', pw)

