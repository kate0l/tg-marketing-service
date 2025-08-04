from django.urls import path

from config.group_channels.views import (
    AddChannelsView,
    CreateGroupView,
    DeleteGroupView,
    GroupDetailView,
    UpdateGroupView,
)

app_name = 'group_channels'

urlpatterns = [
    # сначала фиксированные слова
    path('create/', CreateGroupView.as_view(), name='group_create'),

    # потом вложенные под-пути
    path('<slug:slug>/update/',        UpdateGroupView.as_view(),  name='group_update'),
    path('<slug:slug>/delete/',        DeleteGroupView.as_view(),  name='group_delete'),
    path('<slug:slug>/add-channels/',  AddChannelsView.as_view(),  name='group_add_channels'),

    # и только затем общий «поймай всё остальное»
    path('<slug:slug>/',               GroupDetailView.as_view(),  name='group_detail'),
]
