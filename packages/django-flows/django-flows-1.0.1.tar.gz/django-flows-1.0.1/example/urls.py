# -*- coding: UTF-8 -*-
from example.flows import GetAuthenticatedUser
from flows.handler import FlowHandler

handler = FlowHandler()
handler.register_entry_point(GetAuthenticatedUser)

urlpatterns = handler.urls