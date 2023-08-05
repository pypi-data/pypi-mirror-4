from storages.backends.s3boto import S3BotoStorage

__author__ = 'ajumell'

class S3Storage(S3BotoStorage):
    def __init__(self, *args, **kwargs):
        S3BotoStorage.__init__(self, *args, **kwargs)
        self.secure_urls = False


class SecureS3Storage(S3BotoStorage):
    pass
