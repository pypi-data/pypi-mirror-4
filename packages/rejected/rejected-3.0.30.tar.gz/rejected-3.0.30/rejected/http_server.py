"""HTTP Stats and Control Server"""
from tornado import httpserver
from tornado import ioloop
import logging
import multiprocessing
from tornado import web

logger = logging.getLogger(__name__)


class StatsServer(multiprocessing.Process):

    def run(self):
        pass

    def stop(self):
        pass

