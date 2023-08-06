# Copyright 2013 Joel Dunham
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""Page model"""

from sqlalchemy import Table, Column, Sequence, ForeignKey
from sqlalchemy.types import Integer, Unicode, UnicodeText, Date, DateTime, Boolean
from sqlalchemy.orm import relation, backref
from onlinelinguisticdatabase.model.meta import Base, now

class Page(Base):

    __tablename__ = 'page'
    __table_args__ = {'mysql_charset': 'utf8'}

    def __repr__(self):
        return '<Page (%s)>' % self.id

    id = Column(Integer, Sequence('page_seq_id', optional=True), primary_key=True)
    name = Column(Unicode(255))
    heading = Column(Unicode(255))
    markupLanguage = Column(Unicode(100))
    content = Column(UnicodeText)
    html = Column(UnicodeText)
    datetimeModified = Column(DateTime, default=now)
