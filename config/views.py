from django.shortcuts import render
from django.views.generic.base import View
from config.group_channels.models import Group
from django.db.models import Count


class IndexView(View):
    def get(self, request, *args, **kwargs):
        editorial = (
            Group.objects
                 .filter(is_editorial=True)
                 .annotate(ch_count=Count('channels'))
        )
        return render(request, 'index.html', {'editorial_groups': editorial})
