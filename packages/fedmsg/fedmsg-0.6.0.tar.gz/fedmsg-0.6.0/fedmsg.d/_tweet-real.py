config = dict(
    tweet_intermessage_pause=1,  # seconds
    tweet_hibernate_duration=60 * 3,  # seconds
    tweet_endpoints=[
        # Damn rate limits...
        #tweet_settings=dict(
        #    consumer_key="XSFGNhUmhOsM7jh1UUPUWA",
        #    consumer_secret="rV6PHo9lXuxvKJGqYUeWUoBLMUb1mM0kX22L3Ias",
        #    access_token_key="946934054-UxrRVV4D7nlzYJUYiIdhZ55smUSzMYbP24adjRpz",
        #    access_token_secret="Fw4kEO85Ra6qdSCdjeAuvERLlq3g6asyym6hHBLrGc",
        #),
        dict(
            base_url="http://identi.ca/api",
            consumer_key="a1ecfc33bda40ab34f18c31482011c5e",
            consumer_secret="bbd2653832ba3c3bb2255d78fb6b27c2",
            access_token_key="73a84df717834d65c9df6bd21ed45507",
            access_token_secret="8da41f83396c4cb995b3e0a9862a3862",
        ),
    ],
    bitly_settings=dict(
        api_user="threebean",
        api_key="R_8be5eaf55b05e6294deec857fb2d2ab2",
    ),
)

