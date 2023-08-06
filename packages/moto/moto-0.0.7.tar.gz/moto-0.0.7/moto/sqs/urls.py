from .responses import QueueResponse, QueuesResponse

url_bases = [
    "https?://(.*).amazonaws.com"
]

url_paths = {
    '{0}/$': QueuesResponse().dispatch2,
    '{0}/(?P<account_id>\d+)/(?P<queue_name>\w+)': QueueResponse().dispatch,
}
