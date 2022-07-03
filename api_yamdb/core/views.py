from rest_framework import mixins, viewsets


class CreateListDestroyModelMixinSet(mixins.CreateModelMixin,
                                     mixins.ListModelMixin,
                                     mixins.DestroyModelMixin,
                                     viewsets.GenericViewSet):
    pass
