ADMINS = (
    ("jni", "opensource@jensnistler.de"),
)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

SECRET_KEY = "yourSecretKey"

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "social_auth.backends.facebook.FacebookBackend",
    "social_auth.backends.twitter.TwitterBackend",
    "social_auth.backends.contrib.github.GithubBackend",
)

SOCIAL_AUTH_ENABLED_BACKENDS = ("facebook", "twitter", "github",)

TWITTER_CONSUMER_KEY = "JsMAzcVPLy3qbV0sBxdgfg"
TWITTER_CONSUMER_SECRET = "x4LdsxgH0wvbkgXicfez3YL82onWECiYdsztjGIxDI"

GITHUB_APP_ID = "e46d7c062b3158259cd1"
GITHUB_API_SECRET = "3a8b5f1e09cb0878999fa248bfe3e6a7c4a73539"

FACEBOOK_APP_ID = "325811647445170"
FACEBOOK_API_SECRET = "1de476311666a65128c9a25e6fd24c9b"


