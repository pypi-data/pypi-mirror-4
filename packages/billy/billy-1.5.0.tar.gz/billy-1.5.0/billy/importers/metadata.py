#!/usr/bin/env python
import os
import datetime
import json

from billy.core import db
from billy.importers.utils import prepare_obj

PRESERVED_FIELDS = ('latest_json_url', 'latest_json_date',
                    'latest_csv_url', 'latest_csv_date')


def import_metadata(abbr, data_dir):
    preserved = {}
    old_metadata = db.metadata.find_one({'_id': abbr}) or {}
    for field in PRESERVED_FIELDS:
        if field in old_metadata:
            preserved[field] = old_metadata[field]

    data_dir = os.path.join(data_dir, abbr)
    with open(os.path.join(data_dir, 'metadata.json')) as f:
        data = json.load(f)
        data['_type'] = 'metadata'
        data = prepare_obj(data)

    data['_id'] = abbr
    data.update(preserved)

    data['latest_update'] = datetime.datetime.utcnow()

    db.metadata.save(data, safe=True)
