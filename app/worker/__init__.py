from app.lib.worker import WorkerFunction

from .authors import author_created

functions: list[WorkerFunction] = [author_created]
