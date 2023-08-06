from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from foundry.models import Member

import api


class EverlyticProfile(models.Model):
    member = models.OneToOneField(Member)
    # the Everlytic contact_id used in API requests
    everlytic_id = models.PositiveIntegerField(null=True, unique=True)

    def __unicode__(self):
        return self.member.__unicode__()


@receiver(post_save, sender=Member)
def member_post_save(sender, instance, **kwargs):
    """ Create an EverlyticProfile and store the Everlytic contact_id in
    the profile. (Use it to delete and update the Contact record).
    Create the Everlytic Contact record if it does not exist.
    Set the subscription status of the Contact on the Everlytic mailing
    list.
    """
    ep, created = EverlyticProfile.objects.get_or_create(member=instance)
    if instance.email:
        ep.everlytic_id = api.subscribeUser(instance.last_name,
                                            instance.first_name,
                                            instance.email,
                                            instance.receive_email,
                                            everlytic_id=ep.everlytic_id)
    ep.save()


@receiver(pre_delete, sender=User)
def member_pre_delete(sender, instance, **kwargs):
    """ Delete the EverlyticProfile and unsubscribe from the appropriate
    mailing list on the Everlytic service. Delete the user from the
    Everlytic database.
    """
    try:
        ep = EverlyticProfile.objects.get(member=instance)
        api.deleteEverlyticUser(ep.everlytic_id)
        # ep.delete()
    except EverlyticProfile.DoesNotExist:
        pass
