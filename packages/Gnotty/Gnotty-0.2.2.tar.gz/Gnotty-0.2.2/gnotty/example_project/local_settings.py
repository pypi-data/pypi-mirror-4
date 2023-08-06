DEBUG = True
GNOTTY_LOGIN_REQUIRED = False
GNOTTY_BOT_CLASS = "settings.get_bot"

def get_bot(*args, **kwargs):
    from gnotty.bots import RSSMixin, CommandMixin, BaseBot
    class Bot(RSSMixin, CommandMixin, BaseBot):
        def __init__(self):
            kwargs["feeds"] = ["http://127.0.0.1:4000/atom.xml"]
            super(Bot, self).__init__(*args, **kwargs)
    return Bot()
