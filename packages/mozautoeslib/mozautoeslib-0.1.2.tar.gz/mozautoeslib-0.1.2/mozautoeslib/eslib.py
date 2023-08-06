import logging
# logging.basicConfig(filename='mozautoeslib.log', level=logging.DEBUG)

from pyes import *
from pyes.facets import QueryFacet, StatisticalFacet

class ESLib(object):
  """Class with convenience methods for making common types of
     ElasticSearch queries.
  """

  def __init__(self, server, index, doc_type=None):
    """Initialize an ESLib object with server address, index, and doc_type.
    """

    if not server or not index:
      raise Exception("must specify server and index!")

    self.server = server

    # split the index parameter into read and write indices
    if isinstance(index, list):
      assert(len(index) > 0)
      if len(index) == 1:
        self.index = [index[0], index[0]]
      else:
        self.index = [index[0], index[1]]
    elif isinstance(index, basestring):
      self.index = [index, index]

    self.read_index = self.index[0]
    self.write_index = self.index[1]

    if isinstance(doc_type, list):
      self._doc_type = doc_type
    else:
      self._doc_type = [doc_type]

    self.connection = ES([self.server], timeout=30.0)

  @property
  def doc_type(self):
    if self._doc_type is None:
      raise Exception('doc_type cannot be None')
    return self._doc_type

  @doc_type.setter
  def doc_type(self, value):
    if isinstance(value, list):
      self._doc_type = value
    else:
      self._doc_type = [value]

  def _add_fieldlist_to_boolquery(self, boolquery, fieldlist, add_must):
    """Take an existing boolquery, and add a list of fields to it.  Fields
       are added as 'add_must' if add_must is True, otherwise they are added
       as 'add_must_not'.

       See the query documentation for information on types of fields.
    """

    for key in fieldlist:
      if isinstance(fieldlist[key], list):
        if len(fieldlist[key]) != 2:
          raise Exception("range list must have two members")
        query = RangeQuery(ESRange(key, fieldlist[key][0], fieldlist[key][1]))
      elif isinstance(fieldlist[key], tuple):
        query = FieldQuery()
        query.add(key, " ".join(fieldlist[key]))
      else:
        query = FieldQuery()
        query.add(key, fieldlist[key])
      if add_must:
        boolquery.add_must(query)
      else:
        boolquery.add_must_not(query)

  def _make_bool_query(self, include={}, exclude={}, sort=None):
    """Generate a simple bool query to include fields in 'include', and
       exclude fields in 'exclude'.
    """

    if not include and not exclude:
      return MatchAllQuery()

    boolquery = BoolQuery()
    if include:
      self._add_fieldlist_to_boolquery(boolquery, include, True)
    if exclude:
      self._add_fieldlist_to_boolquery(boolquery, exclude, False)
    if sort:
      boolquery.sort = sort

    return boolquery

  def ORQuery(self, ORItems, size=10000, doc_type=None, useFieldQueries=False,
              fields=None, count=False):
    """Return a list of hits that match any of the combination of terms
       specified in the ORItems list of dicts.

       Example:
         return hits that match any of the following mahine/starttime
         combinations:

       result = eslib.ORQuery([
        {'machine': 'talos-r1', 'starttime': '1306918341'},
        {'machine': 'talos-r2', 'starttime': '1259351812'},
       ])
    """

    if doc_type:
      self.doc_type = doc_type

    resultlist = []

    orList = []
    for item in ORItems:
      andList = []
      for key in item:
        if isinstance(item[key], list):
          andList.append(RangeQuery(ESRange(key, item[key][0], item[key][1])))
        elif useFieldQueries:
          andList.append(QueryFilter(FieldQuery(FieldParameter(key, item[key]))))
        else:
          andList.append(TermFilter(key, item[key]))
      orList.append(ANDFilter(andList))
    orq = ORFilter(orList)

    q = FilteredQuery(MatchAllQuery(), orq)
    s = Search(query=q, fields=fields)

    if count:
      result = self.connection.count(query=q,
                                     indexes=[self.read_index],
                                     doc_types=self.doc_type)
      if not 'count' in result:
        raise Exception("'count' not found in response data")
      return result['count']

    result = self.connection.search(query=s,
                                    size=size,
                                    indexes=[self.read_index],
                                    doc_types=self.doc_type)

    if result and result['hits'] and result['hits']['hits']:
      # partially flatten the data
      for hit in result['hits']['hits']:
        if not '_source' in hit and not 'fields' in hit:
          raise Exception("Neither '_source' nor 'fields' found in response hit")
        resultlist.append(hit['_source'] if '_source' in hit else hit['fields'])

    return resultlist

  def query(self, include={}, exclude={}, size=None, doc_type=None, sort=None,
            withSource=False):
    """Return a list of hits which match all the fields in 'include',
       but none of the fields in 'exclude', up to a maximum of 'size' hits,
       or all hits when 'size' is None.

       Each field in 'include' and 'exclude' can be one of three types:
         - string: the field MUST include that string
         - tuple: the field MUST include any of the strings in the tuple
         - list: the field MUST have a value in the range denoted by the list

       For example, the following query returns all hits that represent
       bug 620598, on the mozilla-central OR tracemonkey trees, in the date
       range 2010-12-21 to 2011-01-05:

  result = eslib.query({'bug': '620598',
                        'tree': ('mozilla-central', 'tracemonkey'),
                        'date': ['2010-12-21', '2011-01-05']})
    """

    if doc_type:
      self.doc_type = doc_type

    resultlist = []

    boolquery = self._make_bool_query(include, exclude)

    if size:
      query_size = size
    else:
      count = self.connection.count(query=boolquery,
                                    indexes=[self.read_index],
                                    doc_types=self.doc_type)
      if not 'count' in count:
        raise Exception("Key ['count'] not found in count response data")
      query_size = count['count']

    # there's no data to return, so don't bother searching
    if query_size == 0:
      return []

    chunk_size = 2000
    for x in range(0,(query_size-1)/chunk_size + 1):
      start = x * chunk_size
      this_size = query_size - x*chunk_size if query_size - x*chunk_size < chunk_size else chunk_size
      if this_size > 0:
        q = Search(query=boolquery, sort=sort, size=this_size, start=start)
        result = self.connection.search(query=q,
                                        indexes=[self.read_index],
                                        doc_types=self.doc_type)

        if result and result['hits'] and result['hits']['hits']:
          # partially flatten the data
          for hit in result['hits']['hits']:
            if withSource:
              resultlist.append(hit)
            else:
              if not '_source' in hit:
                raise Exception("Key ['_source'] not found in response hit")
              resultlist.append(hit['_source'])
        else:
          raise Exception("Key ['hits']['hits'] not found in response data")

    return resultlist

  def aggregates(self, include={}, exclude={}, aggregate_by={}, doc_type=None):
    """Return a count of hits that match all possible combinations of fields
       in aggregate_by.

       Example:

  result = eslib.aggregates(include = {
                                        'tree': ('mozilla-central', 'tracemonkey'),
                                        'date': ['2010-12-21', '2011-01-05']
                                      },
                            aggregate_by = {
                                             'buildtype': ['debug', 'opt', 'pgo'],
                                             'os': ['linux', 'linux64', 'windows', 'osx', 'osx64']
                                           } 
                           )
    """

    if doc_type:
      self.doc_type = doc_type

    resultlist = []
    masterquery = self._make_bool_query(include, exclude)
    q = Search(query=masterquery, size=0)

    aggregate_list = []
    for key in aggregate_by:
      value_list = []
      for value in aggregate_by[key]:
        value_list.append({ key: value })
      aggregate_list.append(value_list)

    r = [[]]
    for x in aggregate_list:
      r = [ i + [y] for y in x for i in r]

    for x in r:
      nameparts = []
      namefields = []
      facetquery = BoolQuery()
      for y in x:
        for key in y:
          nameparts.append(key + ":" + y[key])
          namefields.append({ key: y[key] })
          fieldquery = FieldQuery()
          fieldquery.add(key, y[key])
          facetquery.add_must(fieldquery)
      name = "_".join(nameparts)
      facet = QueryFacet(query = facetquery, name = name)
      q.facet.facets.append(facet)

    result = self.connection.search(query=q,
                                    indexes=[self.read_index],
                                    doc_types=self.doc_type)

    if 'facets' in result:
      return result['facets']

    raise Exception("Key 'facets' not found in response data")

  def statisticalQuery(self, include={}, exclude={}, doc_type=None, fields=None):
    if doc_type:
      self.doc_type = doc_type

    masterquery = self._make_bool_query(include, exclude)
    q = Search(query=masterquery, size=0)

    for field in fields:
      q.facet.facets.append(StatisticalFacet(name=field, field=field))

    result = self.connection.search(query=q,
                                    indexes=[self.read_index],
                                    doc_types=self.doc_type)

    if 'facets' in result:
      return result['facets']

    raise Exception("Key 'facets' not found in response data")

  def frequency(self, include={}, exclude={}, frequency_fields=[], size=30000, doc_type=None):
    """Return a count of the 'size' most frequent terms that are produced
       by a query.

       For example, the following produces a list of the top 50 bugs
       in a date range:

  result = eslib.frequency(include = {
                                        'tree': 'mozilla-central',
                                        'date': ['2010-12-21', '2011-01-05']
                                     },
                           frequency_fields = ["bug"],
                           size = 50
                          )

       Note that date fields in frequency queries are always returned
       in ms since epoch; they can be converted to python datetime objects
       using datetime.datetime.utcfromtimestamp(value/1000).
    """

    if doc_type:
      self.doc_type = doc_type

    boolquery = self._make_bool_query(include, exclude)

    q = Search(query=boolquery, size=0)
    for field in frequency_fields:
      if isinstance(field, basestring):
        q.facet.add_term_facet(field, size=size)
      else:
        q.facet.add_term_facet(field['field'], size=size, script=field.get('script'))

    result = self.connection.search(query=q,
                                    indexes=[self.read_index],
                                    doc_types=self.doc_type)

    if 'facets' in result:
      return result['facets']

    raise Exception("Key 'facets' not found in response data")

  def delete_doc(self, id, doc_type=None):
    if doc_type:
      self.doc_type = doc_type
    self.connection.delete(self.write_index, self.doc_type[0], id)

  def update_field_in_doc(self, id, doc_type, field, value):
    doc = self.connection.get(self.read_index, doc_type, id)
    doc = doc.get('_source')
    doc[field] = value
    self.add_doc(doc, id=id, doc_type=doc_type)

  def add_doc(self, doc, id=None, doc_type=None):
    if doc_type:
      self.doc_type = doc_type
    return self.connection.index(doc, self.write_index, self.doc_type[0], id)

  def delete_index(self):
    try:
      return self.connection.delete_index(self.write_index)
    except Exception:
      pass

  def refresh_index(self):
    self.connection.refresh(indexes=[self.write_index, self.read_index])

