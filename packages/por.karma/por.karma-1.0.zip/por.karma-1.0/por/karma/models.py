# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy import String
from por.models.dashboard import Project

Project.karma_id = Column(String)
