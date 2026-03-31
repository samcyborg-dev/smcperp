from polygon import RESTClient
import pandas as pd

class PolygonFetcher:
    def __init__(self, api_key):
        self.client = RESTClient(api_key)
    
    def get_forex(self, symbol, days=30):
        aggs = self.client.list_aggs(symbol, 1, "minute", 
                                   from_=pd.Timestamp.now() - pd.Timedelta(days=days),
                                   to=pd.Timestamp.now(), limit=50000)
        return pd.DataFrame(aggs)
