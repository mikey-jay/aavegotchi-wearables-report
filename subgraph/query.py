import requests
import time
import vcr

session = requests.Session()

class HTTPStatusError(Exception):
    pass

class SubgraphQueryError(Exception):
    pass

def dict_to_graphql_entities(source):
    entities = []
    for entity in source:
        fields = []
        for field in source[entity]['fields']:
            if type(field) is dict:
                fields.append(dict_to_graphql_entities(field))
            else:
                fields.append(field)
        if 'params' in source[entity].keys():
            params = "(" + dict_to_graphql_params(source[entity]['params']) + ")"
        else:
            params = ''
        entities.append(entity + params + "{" + ",".join(fields) + "}")
    return ",".join(entities)

def dict_to_graphql_query(source):
    return '{' + dict_to_graphql_entities(source) + '}'

def dict_to_graphql_params(source):
    params = []
    for param in source:
        if type(source[param]) is dict:
            params.append('{p}:{{{v}}}'.format(p=param,v=dict_to_graphql_params(source[param])))
        else:
            open_bracket = ''
            close_bracket = ''
            quotes = ''
            
            if type(source[param]) is str:
                quotes = '"'
            elif type(source[param]) is list:
                quotes = '"'
                open_bracket = '['
                close_bracket = ']'
            elif source[param] is None:
                quotes = ''

            if type(source[param]) is bool:
                param_value = 'true' if source[param] else 'false'
            elif source[param] is None:
                param_value = 'null'
            elif type(source[param]) is list:
                param_value = '","'.join(source[param])
            else:
                param_value = source[param]

            params.append('{p}:{ob}{q}{v}{q}{cb}'.format(p=param,v=param_value,q=quotes,ob=open_bracket,cb=close_bracket))    
    return ",".join(params)

class SubgraphQuery(object):
    
    def __init__(self, url, query={}, opts={}):
        first_entity_name = list(query.keys())[0]
        default_pagination_opts = {
            'entity': first_entity_name,
            'key': 'id',
            'order': 'asc',
            'page_size': 100,
            'start_key': 0,
        }
        if 'pagination' in opts.keys():
            pagination_opts = default_pagination_opts | opts['pagination']
        else:
            pagination_opts = default_pagination_opts
        if pagination_opts['order'] == 'desc':
            page_filter_operator = 'lte'
        else:
            page_filter_operator = 'gte'
        paginated_entity_params = {
            'first': pagination_opts['page_size'],
            'orderBy': pagination_opts['key'],
            'orderDirection': pagination_opts['order']
        }
        paginated_entity_where_params = {
            '{key}_{op}'.format(key=pagination_opts['key'],op=page_filter_operator): pagination_opts['start_key']
        }

        paginated_query = query
        # must have a params key
        paginated_query[pagination_opts['entity']] = { 'params': {} } | paginated_query[pagination_opts['entity']]
        paginated_query[pagination_opts['entity']]['params'] | paginated_entity_params
        # params must have a where key
        paginated_query[pagination_opts['entity']]['params'] = { 'where': {} } | paginated_query[pagination_opts['entity']]['params']
        paginated_query[pagination_opts['entity']]['params']['where'] |= paginated_entity_where_params
        
        self.opts = opts | { 'pagination': pagination_opts }
        self.payload = { 'query': '' }
        self.url = url
        self.query = paginated_query
        self.results = []

    def get_next_page(self):
        if self.opts['pagination']['order'] == 'desc':
            page_filter_operator = 'lt'
        else:
            page_filter_operator = 'gt'
        paginated_entity_where_params = {
            '{key}_{op}'.format(key=self.opts['pagination']['key'],op=page_filter_operator): self.response['data'][self.opts['pagination']['entity']][-1][self.opts['pagination']['key']]
        }
        self.query[self.opts['pagination']['entity']]['params']['where'] |= paginated_entity_where_params
        return self.get_result()

    def get_graphql_query(self):
        return dict_to_graphql_query(self.query)

    def get_result(self):
        self.response = self.get_response()
        if 'errors' in self.response:
            raise SubgraphQueryError("Subgraph query failed with response:" + str(self.response) + " " + str(self.payload))
        if 'data' not in self.response.keys():
            raise SubgraphQueryError("Subgraph query returned an unexpected response:" + str(self.response))
        else:
            return self.response['data']

    def get_response(self):
        payload = { 'query': dict_to_graphql_query(self.query) }
        self.payload = payload
        response = session.post(self.url, json=payload)
        if response.status_code != 200:
            raise HTTPStatusError("Subgraph query failed with HTTPS Status Code " + str(response.status_code))
        else:
            return response.json()
    
    def execute(self, use_cache=False):
        DELAY_SECS_BETWEEN_SUBGRAPH_QUERIES = 1
        MAX_SUBGRAPH_PAGES_TO_RETRIEVE = 500
        MAX_RESULTS_DEFAULT = MAX_SUBGRAPH_PAGES_TO_RETRIEVE * 100

        request_count = 0
        entity_name = list(self.query.keys())[0]
        is_first_specified = ('params' in self.query[entity_name].keys()) & ('first' in self.query[entity_name]['params'].keys())
        max_results = self.query[entity_name]['params']['first'] if is_first_specified else MAX_RESULTS_DEFAULT
        
        if use_cache:
            vcr_record_mode = 'new_episodes'
        else:
            vcr_record_mode = 'all'

        gotchi_vcr = vcr.VCR(
            record_mode=vcr_record_mode,
            match_on=['uri', 'method', 'path', 'body']
        )

        with gotchi_vcr.use_cassette('subgraph/cache.yaml') as cass:
            results_page = self.get_result()[entity_name]
            self.results = results_page
            page_count = 1

            while len(results_page) > 0 and len(self.results) < max_results and page_count < MAX_SUBGRAPH_PAGES_TO_RETRIEVE:
                if (cass.play_count <= request_count):
                    time.sleep(DELAY_SECS_BETWEEN_SUBGRAPH_QUERIES)
                request_count = cass.play_count
                results_page = self.get_next_page()[entity_name]
                self.results = self.results + results_page
                page_count = page_count + 1

            return self.results[0:max_results]
