from django.views.generic.base import TemplateView
from mainapp import models

class display_grand_total(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(display_grand_total, self).get_context_data(**kwargs)
        global_stats = {}

        active_clients = models.xsanio_client.objects.filter(
            is_unreachable=False
        ).all()

        for client in active_clients:
            client_lun_cvlabel_entries = models.cvlabel_entry.objects.filter(
                host=client,
            ).all()
            for client_lun_cvlabel_entry in client_lun_cvlabel_entries:
                client_stat_entries = models.stat_entry.objects.filter(
                    host=client,
                    disk=client_lun_cvlabel_entry.disk,
                )

                for client_stat_entry in client_stat_entries:
                    stat_type = client_stat_entry.type.name
                    stat_value = client_stat_entry.value
                    if stat_type in global_stats:
                        global_stats[stat_type] += stat_value
                    else:
                        global_stats[stat_type] = stat_value

        context['global_stats'] = global_stats
        return context
