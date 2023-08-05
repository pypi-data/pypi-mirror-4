from uuid import uuid4

__author__ = 'Dan Ostrowski <dan.ostrowski@gmail.com>'

def simple_hex_key(*args, **kwargs):
    """
    A wrapper around `uuid.uuid4` to adhere to the keygen func API.

    @param args: arguments passed into a create call
    @param kwargs: kwargs passed into a create call
    @rtype: str
    """
    return uuid4().hex