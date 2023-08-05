# -*- coding: utf-8 -*-
from __future__ import absolute_import

from pyramid_rest.mongo import CollectionView

from example.model import Message


class ApplicationUserMessages(CollectionView):

    model_class = Message
