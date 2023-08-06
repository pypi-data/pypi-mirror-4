from djangorestframework.mixins import InstanceMixin, DeleteModelMixin, ListModelMixin
from djangorestframework.views import ModelView
from serene.mixins import CreateModelMixin, ReadModelMixin, UpdateModelMixin, UpdateOrCreateModelMixin, PaginatorMixin


class InstanceModelView(InstanceMixin, ReadModelMixin, UpdateModelMixin, DeleteModelMixin, ModelView):
    pass

class CreatableInstanceModelView(InstanceMixin, ReadModelMixin, UpdateOrCreateModelMixin, DeleteModelMixin, ModelView):
    pass

class PaginatedListOrCreateModelView(ListModelMixin, CreateModelMixin, PaginatorMixin, ModelView):
    pass

class ListOrCreateModelView(ListModelMixin, CreateModelMixin, ModelView):
    pass