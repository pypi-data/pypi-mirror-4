import mexbtcapi
from mexbtcapi.concepts.currencies import USD
from mexbtcapi.concepts.currency import Amount


ten_dollars= Amount(10, USD)
for api in mexbtcapi.apis:
    exchange_rate= api.market(USD).getTicker().sell
    print "At %s I can get %s for my %s (that's %s)"%(api.name, exchange_rate.convert( ten_dollars ), ten_dollars, exchange_rate)

key=    "98b48666-6d56-4031-ea68-8ef0c6b3ddfe"
secret= "A1dcxIWvAiTOhar4091KBoW5mo4ZNwu1QKNFdT3GfFplkYqy3PNbMLANJug0H54awun6dHfc6+QcMbLc7z7pUA=="

'''
account = api.Private(key, secret)
print account.info()
'''
