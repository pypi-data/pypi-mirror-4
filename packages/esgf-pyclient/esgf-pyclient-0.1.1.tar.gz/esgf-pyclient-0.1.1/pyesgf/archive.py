#!/usr/bin/env python
"""
Archive the dataset_ids, filenames and checksums from a particular
search index.

"""

import sys

from pyesgf.search import SearchConnection
from pyesgf.search.context import FileSearchContext
from pyesgf.search.consts import TYPE_FILE

import logging
log = logging.getLogger(__name__)

BATCH_SIZE = 1000
SEARCH_URL = 'http://esgf-index1.ceda.ac.uk/esg-search/search'
CONSTRAINTS = {'project': 'CMIP5'}
#CONSTRAINTS = {}

DISTRIB = True

def main(argv=sys.argv):
    conn = SearchConnection(SEARCH_URL, distrib=DISTRIB)
    ctx = conn.new_context(context_class=FileSearchContext, replica=True, 
                           **CONSTRAINTS)

    hits = ctx.hit_count
    log.info('Records to archive = %s' % hits)

    # Call search manually for extra efficiency.
    query_dict = ctx._build_query()
    for b in range(0, hits, BATCH_SIZE):
        log.info('Sending query for batch %d of %d' % (b, hits / BATCH_SIZE))
        response = conn.send_query(query_dict, limit=BATCH_SIZE, 
                                   offset=b)
        log.info('  Query returned %d documents' % len(response['response']['docs']))
        for doc in response['response']['docs']:
            filename = doc['title']
            try:
                checksum = doc['checksum'][0]
                checksum_type = doc['checksum_type'][0]
                checksum_str = '%s:%s' % (checksum_type, checksum)
            except KeyError:
                checksum_str = 'NONE'

            try:
                tracking_id = doc['tracking_id'][0]
            except KeyError:
                tracking_id = 'NONE'
            try:
                size = doc['size']
            except:
                size = 'NONE'

            dataset_id = doc['dataset_id']

            ds_instance_id, datanode = dataset_id.split('|')
            print ' '.join(str(x) for x in (
                ds_instance_id,
                filename,
                checksum_str,
                size,
                tracking_id,
                ))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
