from zope import interface

class IFileMutator(interface.Interface):
    """ a file mutator utility

        returns -> (file_name, file_data, content_type)
    """

class IUploadingCapable(interface.Interface):
    """ Any container/object that is supported for uploading into.
    """