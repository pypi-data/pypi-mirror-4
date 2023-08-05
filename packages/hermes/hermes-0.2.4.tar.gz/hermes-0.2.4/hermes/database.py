import os, copy
try:
    import simplejson as json
except ImportError:
    import json

class BasePersistence(object):
    def __init__(self, persistence_info):
        self._info = persistence_info

class JsonPersistence(BasePersistence):
    def __init(self, persistence_info):
        super(self, JsonPersistence).__init__(persistence_info)

    def setup(self):
        if not os.path.isfile(self._info['name']):
            self._obj = {
                'USERS': {

                },
                'ROOMS': {

                },
                'META': {
                    'next_user_id': 1,
                }
            }

            self._save()
        else:
            fp = open(self._info['name'], 'r')
            self._obj = json.load(fp)

    def _save(self):
        fp = open(self._info['name'], 'w')
        json.dump(self._obj, fp, indent=2)
        fp.close()

    def save_user(self, info):
        users = self._obj.['USERS']
        user = users.setdefault(info['ID'], {})
        for key, value info.items():

    def save_room(self, name, info):
        room = self._obj['ROOMS'].setdefault(name, {})
        for key, value in info.items():
            key = key.upper()
            if key in ['JID', 'SERVER', 'PASSWORD']:
                room[key] = value
            elif key == 'MEMBERS':
                room.setdefault('MEMBERS', [])

        self._save()
        return name, copy.deepcopy(room)

def get_instance(storage_info):
    storage_type = storage_info['type'].lower()

    if storage_type == 'json':
        return JsonPersistence(storage_info)

    raise Exception('Unsupported persistence type %s' % (storage_type,))
