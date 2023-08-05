from ..decorators import login_required_m


class AuthenticatedViewMixin(object):
    """
    Mixin view that can be used to ensure that any view that
    inherits from it will require that the visitor be signed
    in using the ``login_required`` decorator.
    """
    @login_required_m
    def dispatch(self, *args, **kwargs):
        return super(AuthenticatedViewMixin, self).dispatch(*args, **kwargs)
