from queued_storage.backends import QueuedS3BotoStorage


class QueuedS3BotoMediaStorage(QueuedS3BotoStorage):
    """
    A custom subclass of queued_storage.backends.QueuedFileSystemStorage`
    subclass which uses the S3BotoMediaStorage storage of the incuna
    media storage backend to set the location to "media".
    """

    def __init__(self, remote='incuna.storage_backends.S3BotoMediaStorage', *args, **kwargs):
        super(QueuedS3BotoMediaStorage, self).__init__(remote=remote, *args, **kwargs)

