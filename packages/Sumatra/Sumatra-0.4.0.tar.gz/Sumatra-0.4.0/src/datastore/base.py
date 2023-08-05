"""

"""

import hashlib

IGNORE_DIGEST = "0"*40

class DataStore(object):
    """Base class for data storage abstractions."""
    
    def __getstate__(self):
        """
        Since each subclass has different attributes, we provide this method
        as a standard way of obtaining these attributes, for database storage,
        etc. Returns a dict.
        """
        raise NotImplementedError

    def copy(self):
        return self.__class__(**self.__getstate__())


class DataKey(object):
    
    def __init__(self, path, digest, **metadata):
        self.path = path
        self.digest = digest
        self.metadata = metadata
    
    def __repr__(self):
        return "%s(%s)" % (self.path, self.digest)

    def __eq__(self, other):
        return self.path == other.path and (self.digest == other.digest or IGNORE_DIGEST in (self.digest, other.digest))

    def __ne__(self, other):
        return not self.__eq__(other)
        
        
class DataItem(object):
    """Base class for data item classes, that may represent files or database records."""
    
    def __str__(self):
        return self.path
    
    @property
    def digest(self):
        return hashlib.sha1(self.content).hexdigest()

    def __eq__(self, other):
        if self.size != other.size:
            return False
        elif self.content == other.content: # use digest here?
            return True
        else:
            return self.sorted_content == other.sorted_content
        
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def generate_key(self):    
        return DataKey(self.path, self.digest, mimetype=self.mimetype,
                       encoding=self.encoding, size=self.size)
