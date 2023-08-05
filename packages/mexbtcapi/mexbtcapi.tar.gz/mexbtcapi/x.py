import mexbtcapi
from mexbtcapi.concepts.currencies import USD
from mexbtcapi.concepts.currency import Amount

ten_dollars= Amount(10, USD)
for api in mexbtcapi.apis:
    exchange_rate= api.market(USD).getTicker().sell
print ("At {0} I can get {1} for my {2} (that's {3})".format(api.name, exchange_rate.convert( ten_dollars ), ten_dollars, exchange_rate))
