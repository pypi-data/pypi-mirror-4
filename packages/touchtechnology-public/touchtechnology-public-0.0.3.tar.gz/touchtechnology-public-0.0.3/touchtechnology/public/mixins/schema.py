class SouthTripleMixin(object):
    """
    A mixin to make fields that customise the default Django fields
    play nice with South migrations.
    """
    def south_field_triple(self):
        """
        Assumes that the mixin will be earlier than the Django field
        in the inheritance declaration; eg.

        >>> class SpecialField(SouthTripleMixin, models.CharField):
        ...     pass
        """
        from south.modelsinspector import introspector
        base = self.__class__.__bases__[-1]
        field_class = "%s.%s" % (base.__module__, base.__name__)
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)
