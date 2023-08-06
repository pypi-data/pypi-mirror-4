# -*- coding: utf-8 -*-

"""

tinys3.request_factory
~~~~~~~~~~~~~~~~~~~~~~

Generates Request objects for various S3 requests

"""


from datetime import timedelta
import mimetypes
from requests import Request

# A fix for windows pc issues with mimetypes
# http://grokbase.com/t/python/python-list/129tb1ygws/mimetypes-guess-type-broken-in-windows-on-py2-7-and-python-3-x
mimetypes.init([])


class RequestFactory(object):
    """

    """

    @classmethod
    def bucket_url(cls, key, bucket, ssl=False):
        protocol = 'https' if ssl else 'http'

        return "%s://s3.amazonaws.com/%s/%s" % (protocol, bucket, key.lstrip('/'))

    @classmethod
    def upload_request(cls, key, local_file, auth,
                       bucket, expires=None, content_type=None,
                       public=True, extra_headers=None, ssl=False):
        # get the url
        url = cls.bucket_url(key, bucket, ssl=ssl)

        # set the content type
        content_type = content_type or mimetypes.guess_type(key)[0] or 'application/octet-stream'

        # Handle content expiration
        if expires == 'max':
            expires = timedelta(seconds=31536000)
        elif isinstance(expires, int):
            expires = timedelta(seconds=expires)
        else:
            expires = expires

        # set headers
        headers = {'Content-Type': content_type}

        if public:
            headers['x-amz-acl'] = 'public-read'

        if expires:
            headers['Cache-Control'] = "max-age=%d" % cls.get_total_seconds(expires) + ', public' if public else ''

        # update headers with the extras
        if extra_headers:
            headers.update(extra_headers)

        return Request(method='PUT', url=url, headers=headers, auth=auth, data=local_file)

    @classmethod
    def copy_request(cls, from_key, from_bucket, to_key, to_bucket, metadata, public, auth, ssl=False):
        from_key = from_key.lstrip('/')
        to_key = to_key.lstrip('/')

        headers = {
            'x-amz-copy-source': "/%s/%s" % (from_bucket, from_key),
            'x-amz-metadata-directive': 'COPY' if not metadata else 'REPLACE'
        }

        if public:
            headers['x-amz-acl'] = 'public-read'

        if metadata:
            headers.update(metadata)

        return Request(method='PUT',
                       url=cls.bucket_url(to_key, to_bucket, ssl=ssl),
                       headers=headers, auth=auth)

    @classmethod
    def update_metadata_request(cls, key, metadata, bucket, public, auth, ssl=False):
        return cls.copy_request(key, bucket, key, bucket, metadata, public, auth, ssl=ssl)

    @classmethod
    def delete_request(cls, key, bucket, auth, ssl=False):
        url = cls.bucket_url(key, bucket, ssl=ssl)

        return Request(method='DELETE', url=url, auth=auth)

    @classmethod
    def list_request(cls, bucket=None, marker=None, prefix=None, page_size=1000):
        pass

    @classmethod
    def get_total_seconds(cls, timedelta):
        """
        Support for getting the total seconds from a time delta (Required for python 2.6 support)
        """
        return timedelta.days * 24 * 60 * 60 + timedelta.seconds