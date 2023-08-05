import logging
logger = logging.getLogger(__name__)

class BaseObject(object):

    def __getattribute__(self,name):
        '''When reffered to self.X, this function first searches self.X, followed
        by self._X.  And only when both self.X and self._X is not set, provider()
        will be invoked, which will be set self._X.
        '''

        # If self.X is set.
        try:
            object.__getattribute__(self, name)
            return object.__getattribute__(self, name)
        except AttributeError, e:
            logger.debug("Attibute self.%s is not set. Try to check self._%s" % (name,name))

        # If self._X is set.
        try:
            object.__getattribute__(self, "_"+name)
            return object.__getattribute__(self, "_"+name)
        except AttributeError, e:
            logger.debug("Attibute self._%s is not set. Try to invoke provider" % (name,))

        # We cannot find either self.X or self._X
        for attr_name,provider in self.prop_info:
            if attr_name == name:
                provider()
                break

        # Here, we should have self._X
        try:
            object.__getattribute__(self, "_"+name)
            return object.__getattribute__(self, "_"+name)
        except AttributeError, e:
            raise Exception("Oops, provider cannot provide self._%s", name)

    def refresh(self):
        '''Our implementation of __getattribute__ is just like a cache. So
        if the attribute should change, it is necessary to forget everything.
        This function do this work.
        '''
        for attr_name,provider in self.prop_info:
            try:
                delattr(self, "_"+attr_name)
            except:
                pass
        
