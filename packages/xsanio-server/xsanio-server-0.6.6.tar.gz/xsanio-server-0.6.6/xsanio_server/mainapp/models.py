from django.db import models


class xsanio_client(models.Model):
    """Can be a client, can be an MDC -- the only thing that matters
    is xsanio_client being installed on the
    machine

    """
    host_name = models.CharField(max_length=255)
    ip_address = models.IPAddressField()
    port = models.IntegerField(default=8090)
    is_unreachable = models.BooleanField(default=True)
    has_client_installed = models.BooleanField(default=False)
    latest_update = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.host_name


class stat_type(models.Model):
    """Types of statistics we have. E.g. I/O per second, bytes read per second and so on.

    """
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

class stat_entry(models.Model):
    """Stat entry is a specific value of a specific task type for a specific host

    """
    type = models.ForeignKey(stat_type)
    host = models.ForeignKey(xsanio_client)
    disk = models.CharField(max_length=255)
    value = models.FloatField(null=True, blank=True, default=0.0)
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s: %s for %s" % (self.host, self.type, self.disk)

class cvlabel_entry(models.Model):
    """Stores one 'disk name' -- 'label name' relationship for a specific host

    """
    host = models.ForeignKey(xsanio_client)
    disk = models.CharField(max_length=255)
    label = models.CharField(max_length=255)

    def __unicode__(self):
        return "%s: %s " % (self.host, self.disk)

class xsan_volume(models.Model):
    """We need to remember, which LUNs each volume is composed of

    """
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

class xsan_volume_lun(models.Model):
    """An entry for each LUN that is assigned to particular Xsan volume

    """
    label = models.CharField(max_length=255)
    volume = models.ForeignKey(xsan_volume)

    def __unicode__(self):
        return self.label
