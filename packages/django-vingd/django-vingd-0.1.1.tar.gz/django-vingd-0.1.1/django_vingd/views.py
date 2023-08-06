from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.views.generic import View

from .models import VingdOrder, VingdMeta
from .util import VingdException

class OrderView(View):
    def handle_exception(self, e):
        raise

    def post(self, request, nametag):
        # Fetchnig class name from request.
        try:
            vo = VingdMeta.get_cls_from_nametag(nametag)()
            vo.request = request
        except Exception as e:
            return self.handle_exception(e)
        
        # Uses class specific exception handling.
        return vo.order()

class VerifyView(View):
    def handle_exception(self, e):
        raise

    def get(self, request):
        # Fetching order from context.
        try:
            vo = VingdOrder.get_order_from_context(request)
        except Exception as e:
            return self.handle_exception(e)

        # Uses class specific exception handling.
        return vo.verify()
