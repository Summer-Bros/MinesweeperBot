import os

from .bot import ProjectBot


ProjectBot().run(os.environ["BOT_TOKEN"])
