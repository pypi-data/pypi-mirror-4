import urllib2
import feedparser
from urllib import urlencode
from datetime import datetime, timedelta
from hashlib import sha1

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch

from djpubsubhubbub import signals
from djpubsubhubbub.config import Config

DEFAULT_LEASE_SECONDS = 2592000 # 30 days in seconds


class SubscriptionManager(models.Manager):

    def do_action(self, topic, hub=None, callback=None, lease_seconds=None,
                  mode='subscribe', verify='sync', debug=False):
        config = Config()
        if hub is None:
            hub = self._get_hub(topic)

        if hub is None:
            raise TypeError(
                'hub cannot be None if the feed does not provide it')

        if lease_seconds is None:
            lease_seconds = getattr(settings, 'PUBSUBHUBBUB_LEASE_SECONDS',
                                   DEFAULT_LEASE_SECONDS)

        subscription, created = self.get_or_create(
            hub=hub, topic=topic)
        signals.pre_subscribe.send(sender=subscription, created=created)
        subscription.set_expiration(lease_seconds, run_save=False)
        token = subscription.generate_token(mode)
        headers = config.get_extra_hub_headers(topic, hub)

        if callback is None:
            try:
                callback_path = reverse('pubsubhubbub_callback',
                                        args=(subscription.pk,))
            except NoReverseMatch:
                raise TypeError(
                    'callback cannot be None if there is not a reversible URL')
            else:
                callback = 'http://%s%s' % (
                    config.get_default_callback_host(topic, hub),
                    callback_path
                )

        response = self._send_request(hub, {
                'mode': mode,
                'callback': callback,
                'topic': topic,
                'verify': verify,
                'verify_token': token,
                'lease_seconds': lease_seconds,
            }, headers, debug)

        info = response.info()
        info.status = response.code
        if debug:
            print 'Info:\n%s\n\n' % str(info)

        if info.status not in [204, 202]:
            # 204 is sync verification
            # 202 is async verification
            error = response.read()
            raise urllib2.URLError(
                'error with mode "%s" to %s on %s:\n%s' % \
                                            (mode, topic, hub, error)
            )

        return subscription
    
    def subscribe(self, topic, **kwargs):
        return self.do_action(topic, mode='subscribe', **kwargs)
    
    def unsubscribe(self, topic, **kwargs):
        return self.do_action(topic, mode='unsubscribe', **kwargs)

    def _get_hub(self, topic):
        parsed = feedparser.parse(topic)
        for link in parsed.feed.links:
            if link['rel'] == 'hub':
                return link['href']

    def _send_request(self, url, data, headers={}, debug=False):
        def data_generator():
            for key, value in data.items():
                key = 'hub.' + key
                if isinstance(value, (basestring, int)):
                    yield key, str(value)
                else:
                    for subvalue in value:
                        yield key, value

        encoded_data = urlencode(list(data_generator()))
        #headers.update({'Content-Length': (len(encoded_data) + 2)})
        if debug:
            print 'Sending:\n%s\n%s\n%s\n\n' % (url, encoded_data, headers)

        req = urllib2.Request(url, encoded_data, headers=headers)
        return urllib2.urlopen(req)


class Subscription(models.Model):
    hub = models.URLField()
    topic = models.URLField()
    verified = models.BooleanField(default=False)
    verify_token = models.CharField(max_length=60)
    lease_expires = models.DateTimeField(default=datetime.now)
    
    is_subscribed = models.BooleanField(default=False)
    
    date = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(default=datetime.now)

    objects = SubscriptionManager()

    class Meta:
        ordering = ('id',)
        #unique_together = (('hub', 'topic'),)

    def __unicode__(self):
        if self.verified:
            verified = u'verified'
        else:
            verified = u'unverified'
        return u'to %s on %s: %s' % (
            self.topic, self.hub, verified)

    def __str__(self):
        return str(unicode(self))

    def set_expiration(self, lease_seconds, run_save=True):
        self.lease_expires = datetime.now() + timedelta(
            seconds=lease_seconds)
        if run_save:
            self.save()

    def generate_token(self, mode, run_save=True):
        assert self.pk is not None, \
            'Subscription must be saved before generating token'
        token = mode[:20] + sha1('%s%i%s' % (
                settings.SECRET_KEY, self.pk, mode)).hexdigest()
        self.verify_token = token
        if run_save:
            self.save()
        return token
    
    def save(self, *args, **kwargs):
        if self.id:
            self.updated = datetime.now()
        super(Subscription, self).save(*args, **kwargs)
