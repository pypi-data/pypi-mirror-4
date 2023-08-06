from ming.odm import ThreadLocalODMSession, Mapper
import os
from ming import create_datastore, Session

mainsession = Session()
DBSession = ThreadLocalODMSession(mainsession)

class MingPlug(object):
    def __init__(self, mongo_uri):

        if mongo_uri[0]=='$':
            mongo_uri = os.getenv(mongo_uri[1:])
        self.mongo_engine = create_datastore(mongo_uri)

    def __call__(self, app, core, config):
        mainsession.bind = self.mongo_engine

        Mapper.compile_all()

        for mapper in Mapper.all_mappers():
            mainsession.ensure_indexes(mapper.collection)

        return app