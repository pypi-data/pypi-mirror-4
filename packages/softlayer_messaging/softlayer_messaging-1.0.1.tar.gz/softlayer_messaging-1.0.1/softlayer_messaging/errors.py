""" See COPYING for license information """


class ResponseError(Exception):
    """ Exception thrown whenever a client error occurs """

    @property
    def errors(self):
        if len(self.args) > 1:
            return self.args[1]

    def __repr__(self):
        if self.errors:
            return "%s -> %r" % (self.args[0], self.errors)
        else:
            return "%s" % (self.args[0], )

    def __str__(self):
        return self.__repr__()


class Unauthenticated(ResponseError):
    """ Exception thrown whenever a client cannot be Unauthenticated """
    pass
