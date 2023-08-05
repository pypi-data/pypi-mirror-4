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

        # Registered "fedmsgbot" on identi.ca with pw
        # "peopleeatingbaconallacrossthen@tion!"
        #auth request key is: c92734bfc5719d7f897f7ff633943eba
        #auth request secret is: 4593cba3774f4970d4c394be7df67544
        #auth access key is: c1096c0d303be4f222bbdb9122f48453
        #auth access secret is: 94dbaf379032af6396333bdd2358a262

        dict(
            base_url="http://identi.ca/api",
            consumer_key="c92734bfc5719d7f897f7ff633943eba",
            consumer_secret="4593cba3774f4970d4c394be7df67544",
            access_token_key="c1096c0d303be4f222bbdb9122f48453",
            access_token_secret="94dbaf379032af6396333bdd2358a262",
        ),
    ],

    # Email on fedmsgbot is set to admin@fedoraproject.org
    # password is "peopleeatingbaconallacrossthen@tion!"
    bitly_settings=dict(
        api_user="fedmsgbot",
        api_key="R_a7da60f2a474644c4222e71eac32cb12",
    ),
)

