"""
Some storage classes for use with S3.

S3MediaStorage & S3StaticStorage both set the folder to use within the bucket.
Use like so:
    DEFAULT_FILE_STORAGE = 'incuna.storages.S3MediaStorage'
    STATICFILES_STORAGE = 'incuna.storages.S3StaticStorage'

Thus allowing the use of one bucket for both media and static.
"""
import os

from storages.backends.s3boto import S3BotoStorage


class S3MediaStorage(S3BotoStorage):
    def __init__(self, *args, **kwargs):
        super(S3MediaStorage, self).__init__(*args, **kwargs)
        self.location = os.path.join(self.location, 'media')


class S3StaticStorage(S3BotoStorage):
    def __init__(self, *args, **kwargs):
        super(S3StaticStorage, self).__init__(*args, **kwargs)
        self.location = os.path.join(self.location, 'static')

