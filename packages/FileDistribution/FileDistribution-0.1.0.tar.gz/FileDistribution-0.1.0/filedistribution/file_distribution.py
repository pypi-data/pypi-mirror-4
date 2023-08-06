import os.path

__author__ =  'Adam Kubica (caffecoder) <caffecoder@kaizen-step.com>'

class FileDistribution:
    """
    Class for manage hashed file distribution. 
    """

    def __init__(self,prefix):
        """
        Creates new instance with directory prefix.

        Arguments:
        prefix - directory prefix.
        """
        self.ext = '.dat'
        self.prefix = os.path.normpath(prefix)
        self.path = self.prefix

    def set_extension(self,ext):
        """
        Arguments:
        ext - file extension.
        """
        if (len(ext) and not ext.startswith('.')):
            self.ext = '.' + ext
        else:
            self.ext = ext

    def get_path(self):
        """
        Returns Destination path.
        """
        return self.path

    def hex_path(self,id):
        """
        Arguments:
        id - database file ID etc.
        """
        hex = "%x" % int(id)

        if (len(hex) % 2):
            hex = '0%s' % (hex)

        j = len(hex)-2

        while (j > 1):
            hex = os.path.join(hex[:j], hex[j:])
            j = j-2

        self.path = os.path.join(self.prefix, hex)
        self.path += self.ext

    def rename_from(self,path):
        """
        Arguments:
        path - source file path.

        Returns true if rename was successful.
        """
        os.renames(path, self.path)
