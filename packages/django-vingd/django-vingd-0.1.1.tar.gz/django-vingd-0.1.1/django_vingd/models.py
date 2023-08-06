from django.conf import settings
from django.db import models, IntegrityError
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils import timezone

from . import VINGD_CLIENT
from . import consts

from .util import encode64, decode64, append_get_params, HttpResponseJSON, VingdException

import datetime

class VingdMeta():
    VINGD_ORDER_CLSES = {}

    @staticmethod
    def register(Clses):
        for Cls in Clses:
            VingdMeta.VINGD_ORDER_CLSES[Cls.get_nametag()] = Cls

    @staticmethod
    def get_cls_from_nametag(type):
        cls = VingdMeta.VINGD_ORDER_CLSES.get(type)
        if not cls:
            raise VingdException('Unknown Vingd Order type!')
        return cls

class DateModel(models.Model):
    date_modified = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract=True

    def __unicode__(self):
        return str(self.id)

class StoredVingdObject(DateModel):
    label = models.CharField(max_length=128)
    vingd_mode = models.CharField(max_length=512)
    display_name = models.CharField(max_length=128)
    vingd_object_id = models.IntegerField(null=True)
    
    class Meta:
        unique_together = (('label', 'vingd_mode', ), )
    
    @staticmethod
    def fetch(label, display_name):
        os = list(StoredVingdObject.objects.filter(label=label, vingd_mode=consts.VINGD_MODE))
        if os:
            return os[0].vingd_object_id
        url = settings.SITE_URL + reverse('vingd_verify')
        try:
            vingd_object_id = VINGD_CLIENT.create_object(display_name, url)
        except:
            raise
            raise VingdException('Failed adding Vingd object!')
        o = StoredVingdObject(
            label = label,
            vingd_mode = consts.VINGD_MODE,
            display_name = display_name,
            vingd_object_id = vingd_object_id,
        )
        try:
            o.save(force_insert=True)
        except IntegrityError:
            o = StoredVingdObject.objects.get(label=label)
        return o.vingd_object_id
    
class StoredVingdOrder(DateModel):
    label = models.CharField(max_length=128)
    vingd_mode = models.CharField(max_length=512)
    vingd_amount = models.IntegerField()
    display_name = models.CharField(max_length=128)
    vingd_order_id = models.IntegerField(null=True)
    vingd_object_id = models.IntegerField(null=True)
    date_expires = models.DateTimeField()
    
    class Meta:
        unique_together = (('label', 'vingd_mode', 'vingd_amount', ), )
    
    @staticmethod
    def fetch(label, vingd_amount, display_name):
        os = list(StoredVingdOrder.objects.filter(label=label, vingd_mode=consts.VINGD_MODE, vingd_amount=vingd_amount))
        if os:
            return os[0].vingd_order_id
        vingd_object_id = StoredVingdObject.fetch(label, display_name)
        date_expires = timezone.now()+ datetime.timedelta(days=1365)
        try:
            vingd_order_id = VINGD_CLIENT.create_order(vingd_object_id, vingd_amount, date_expires)['id']
        except:
            raise
            raise VingdException('Failed adding Vingd object!')
        o = StoredVingdOrder(
            label = label,
            vingd_mode = consts.VINGD_MODE,
            vingd_amount = vingd_amount,
            display_name = display_name,
            vingd_object_id = vingd_object_id,
            vingd_order_id = vingd_order_id,
            date_expires = date_expires,
        )
        try:
            o.save(force_insert=True)
        except IntegrityError:
            o = StoredVingdOrder.objects.get(label=label, vingd_amount=vingd_amount)
        return o.vingd_order_id

class VingdOrder(DateModel):
    class Meta:
        abstract = True
        
    request = None

    ORDER_NAMETAG = None

    vingd_amount = models.IntegerField(null=True)
    vingd_order_id = models.IntegerField(null=True)
    vingd_is_paid = models.BooleanField(default=False)
    vingd_date_paid = models.DateTimeField(null=True)
    vingd_transferid = models.IntegerField(null=True)
    vingd_purchaseid = models.IntegerField(null=True)
    vingd_huid = models.CharField(null=True, max_length=256)
    vingd_ip = models.CharField(null=True, max_length=256)
    
    vingd_is_refunded = models.NullBooleanField()
    vingd_refund_date = models.DateTimeField(null=True)
    vingd_refund_tid = models.IntegerField(null=True)
    
    @classmethod
    def get_nametag(Cls):
        return Cls.ORDER_NAMETAG or Cls.__name__
    
    #
    # ORDER ROUTINES.
    #
    def order(self):
        try:
            return self.order_pipeline()
        except Exception as e:
            return self.handle_exception(e)

    def order_pipeline(self):
        response = self.take_order()
        if response:
            return response
        self.set_order_data()
        self.save(force_insert=True)
        if self.vingd_amount==0:
            # free, accept_order without vingd confiramtion
            self.accept_order()
            return self.success_response()
        # not free, go to vingd
        return self.redirect_to_vingd()

    def set_order_data(self):
        self.vingd_amount = self.get_vingd_amount()
        if self.vingd_amount is None or self.vingd_amount<0:
            raise VingdException('Invalid vingd price!')
        self.vingd_order_id = self.get_order_id()
        if self.vingd_amount and not self.vingd_order_id:
            raise VingdException('Invalid vingd order id definition!')
        self.vingd_ip = self.request.META.get('REMOTE_ADDR')

    def redirect_to_vingd(self):
        vingd_url = self.get_vingd_url()
        if self.request.is_ajax():
            return HttpResponseJSON({
                'ok': True,
                'vingd_url': vingd_url,
            })
        return HttpResponseRedirect(vingd_url)

    def get_vingd_url(self):
        url = '%s/orders/%s/add/' % (consts.VINGD_FRONTEND, self.vingd_order_id)
        params = {
            'context': self.encode_order_context(),
            'object_url': '%s%s' % (settings.SITE_URL, reverse('vingd_verify')),
            'site_url': settings.SITE_URL,
        }
        return append_get_params(url, params)

    def encode_order_context(self):
        return encode64({
            'nametag': self.get_nametag(),
            'id': self.id
        })

    # each label will generate seaparate vingd object
    # for better performace use single label per VingdOrder class
    # i.e. dont override this
    def get_label(self):
        return self.get_nametag()
    
    # stored on first call for given label, cannot be changed later
    # to have dynamic display names must use dynamic label
    def get_display_name(self):
        return "Some vingd object"

    def get_order_id(self):
        return StoredVingdOrder.fetch(self.get_label(), self.get_vingd_amount(), self.get_display_name())

    #
    # VERIFY ROUTINES.
    #
    def verify(self):
        try:
            return self.verify_pipeline()
        except Exception as e:
            return self.handle_exception(e)
    
    def verify_pipeline(self):
        self.is_ready_to_verify()
        self.vingd_verify()
        self.accept_order()
        self.vingd_commit()
        return self.success_response()

    @staticmethod
    def get_order_from_context(request):
        context = request.GET.get('context')
        try:
            dict = decode64(context)
            nametag = dict.get('nametag')
            id = dict.get('id')
            cls = VingdMeta.get_cls_from_nametag(nametag)
            vo = cls.objects.get(id=id)
        except:
            raise
            raise VingdException('Failed to retrieve object from context %s!' % context)
        vo.request = request
        return vo

    def is_ready_to_verify(self):
        if self.vingd_is_paid:
            raise VingdException('This order is already completed!')

    def vingd_verify(self):
        request = self.request
        try:
            oid = int(request.GET['oid'])
            tid = request.GET['tid']
        except:
            raise VingdException('Invalid verify purchase parameters!')
        try:
            data = VINGD_CLIENT.purchase_verify(oid, tid)
        except:
            raise
            raise VingdException('Exception on vingd broker: get object token: oid %s, tid %s' % (oid, tid))
        vingd_order_id = data['orderid']
        vingd_huid = data['huid']
        vingd_transferid = data['transferid']
        vingd_purchaseid = data['purchaseid']
        if vingd_order_id!=self.vingd_order_id:
            raise VingdException('Invalid vingd order id: %s, %s' % (vingd_order_id, data))
        self.vingd_is_paid = True
        self.vingd_huid = vingd_huid
        self.vingd_transferid = vingd_transferid
        self.vingd_purchaseid = vingd_purchaseid
        self.vingd_date_paid = timezone.now()
        self.save(force_update=True)
    
    def vingd_commit(self):
        try:
            response = VINGD_CLIENT.purchase_commit(self.vingd_purchaseid, self.vingd_transferid)
        except:
            raise
            raise VingdException('Exception on broker - purchase commit: %s' % self.id)

    def success_response(self):
        request = self.request
        if request.is_ajax():
            return HttpResponseJSON({
                'ok': True,
            })
        return HttpResponseRedirect('/')

    def take_order(self):
        pass

    def get_vingd_amount(self):
        pass

    def accept_order(self):
        pass

    def handle_exception(self, e):
        raise

    def refund(self):
        count = self.__class__.objects.filter(id=self.id, vingd_is_paid=True).exclude(vingd_is_refunded=True).update(vingd_is_refunded=True)
        if not count:
            raise VingdException('Vingd transaction already refunded!')
        self.vingd_is_refunded = True
        reward = VINGD_CLIENT.reward_user(
            huid_to = self.vingd_huid,
            amount = self.vingd_amount,
            description = 'Refund',
        )
        self.vingd_refund_date = timezone.now()
        self.vingd_refund_tid = reward['transfer_id']
        self.save(force_update=True)
