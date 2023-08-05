from django.views.generic import ListView
from django.views.generic import DetailView
from mainapp import models


class display_client_list(ListView):
    template_name = 'client_list.html'
    model = models.xsanio_client


class display_client_detail(DetailView):
    template_name = 'client_detail.html'
    model = models.xsanio_client

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(display_client_detail, self).get_context_data(**kwargs)

        disks_iodata = {}

        client = models.xsanio_client.objects.get(pk=self.kwargs['pk'])
        client_stat_entries = models.stat_entry.objects.filter(
            host=client,
        )

        for client_stat_entry in client_stat_entries:
            disk_name = client_stat_entry.disk

            if disk_name not in disks_iodata:
                disks_iodata[disk_name] = {}

            disk_iodata = disks_iodata[disk_name]
            disk_iodata[client_stat_entry.type.name] = client_stat_entry.value

        disks_iodata_array = []
        for disk_name in disks_iodata:
            result = {}
            #   Is there a cvlabel for this disk?
            disk_cvlabel = models.cvlabel_entry.objects.filter(
                host=client,
                disk=disk_name,
            ).all()

            if disk_cvlabel:
                result['disk_name'] = disk_cvlabel[0].label
            else:
                result['disk_name'] = disk_name

            for stat_type in models.stat_type.objects.all():
                result[stat_type.name] = disks_iodata[disk_name][stat_type.name]

            disks_iodata_array.append(result)

        #   Sorting!
        if 'stat_type_order' in self.kwargs:
            stat_type_order = self.kwargs['stat_type_order']
            disks_iodata_array = reversed(sorted(disks_iodata_array, key=lambda k: k[stat_type_order]))

        global_stats = {}
        for stat_type in models.stat_type.objects.all():
            stat_name = stat_type.name
            for disk_name in disks_iodata:
                if stat_name not in global_stats:
                    global_stats[stat_name] = disks_iodata[disk_name][stat_name]
                else:
                    global_stats[stat_name] += disks_iodata[disk_name][stat_name]

        context['disks_iodata'] = disks_iodata_array
        context['global_stats'] = global_stats
        return context
