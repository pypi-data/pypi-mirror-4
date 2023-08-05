from django.views.generic import ListView
from django.views.generic import DetailView
from mainapp import models
import logging


LOGGER = logging.getLogger(__name__)
LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOG_LEVEL = logging.ERROR


def has_all_stats(client_data):
    for stat_type in models.stat_type.objects.all():
        stat_type_name = stat_type.name
        if stat_type_name not in client_data:
            return False
    return True


class display_volume_list(ListView):
    template_name = 'volume_list.html'
    model = models.xsan_volume


class display_volume_detail(DetailView):
    template_name = 'volume_detail.html'
    model = models.xsan_volume

    def get_context_data(self, **kwargs):
        logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)

        # Call the base implementation first to get a context
        context = super(display_volume_detail, self).get_context_data(**kwargs)

        #   This will be passed to the template
        all_clients_data = []
        global_stats = {}
        xsan_volume = models.xsan_volume.objects.get(pk=self.kwargs['pk'])

        #   Now we read and compile the I/O data for all present clients
        active_clients = models.xsanio_client.objects.filter(
            is_unreachable=False
        ).all()
        for client in active_clients:
            LOGGER.info('Calculating total stats for client %s', client.host_name)
            client_data = {}
            client_data['client_hostname'] = client.host_name
            client_data['client_id'] = client.id
            volume_luns = models.xsan_volume_lun.objects.filter(
                volume=xsan_volume
            ).all()
            #   grab stats for each volume's LUN and add them to total client stats
            for volume_lun in volume_luns:
                LOGGER.info('Calculating stats for LUN %s', volume_lun.label)
                client_lun_cvlabel_entries = models.cvlabel_entry.objects.filter(
                    host=client,
                    label=volume_lun.label
                ).all()
                if len(client_lun_cvlabel_entries) == 1:
                    client_lun_cvlabel_entry = client_lun_cvlabel_entries[0]
                    client_stat_entries = models.stat_entry.objects.filter(
                        host=client,
                        disk=client_lun_cvlabel_entry.disk,
                    )

                    for client_stat_entry in client_stat_entries:
                        LOGGER.info('Adding stat entry: %s', client_stat_entry.type.name)
                        stat_type = client_stat_entry.type.name
                        stat_value = client_stat_entry.value
                        if stat_type in client_data:
                            client_data[stat_type] += stat_value
                        else:
                            client_data[stat_type] = stat_value

            all_clients_data.append(client_data)

        for client_data in all_clients_data:
            for stat_type in client_data:
                stat_value = client_data[stat_type]

                if stat_type in global_stats:
                    global_stats[stat_type] += stat_value
                else:
                    global_stats[stat_type] = stat_value


        #   Remove clients that don't have all stats defined
        #   TODO: find a better way to resolve this!
        all_clients_data[:] = [x for x in all_clients_data if has_all_stats(x)]

        #   Sorting!
        if 'stat_type_order' in self.kwargs:
            stat_type_order = self.kwargs['stat_type_order']
            all_clients_data = reversed(sorted(all_clients_data, key=lambda k: k[stat_type_order]))

        context['clients_data'] = all_clients_data
        context['global_stats'] = global_stats
        return context

