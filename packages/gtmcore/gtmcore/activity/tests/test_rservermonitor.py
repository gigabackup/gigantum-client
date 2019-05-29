import json
from pkg_resources import resource_filename
import os
import requests
from gtmcore.activity.tests.fixtures import get_redis_client_mock, redis_client, MockSessionsResponse
from gtmcore.fixtures import mock_labbook
from gtmcore.container.utils import infer_docker_image_name
from gtmcore.activity import ActivityStore, ActivityType, ActivityDetailType

from gtmcore.activity.monitors.monitor_rserver import RServerMonitor, RStudioServerMonitor

def mock_ip(key):
    return "172.0.1.2"

class TestRServerMonitor(object):

    def test_setup(self, redis_client):
        """Test getting the supported names of the dev env monitor"""
        monitor = RServerMonitor()

        assert len(monitor.get_dev_env_name()) == 1
        assert 'rstudio' in monitor.get_dev_env_name()


class TestRStudioServerMonitor(object):

    def test_init(self, redis_client, mock_labbook):
        """Test getting the supported names of the dev env monitor"""
    
        server_monitor = RStudioServerMonitor("test", "test", mock_labbook[2].name,
                                            "52f5a3a9", config_file=mock_labbook[0])
        assert len(server_monitor.processors) == 6

    def test_code_and_image(self, redis_client, mock_labbook):
        """Test reading a log and storing a record"""
    
        # create a server monitor 
        server_monitor = RStudioServerMonitor("test", "test", mock_labbook[2].name,
                                            "foo:activity_monitor:52f5a3a9", config_file=mock_labbook[0])

        mitmlog = open(f"{os.path.dirname(os.path.realpath(__file__))}/52f5a3a9.rserver.dump", "rb")

        # Read activity and return an aggregated activity record
        server_monitor.process_activity(mitmlog)
        # call processor
        server_monitor.store_record() 

        a_store = ActivityStore(mock_labbook[2])
        ars = a_store.get_activity_records()

        # details object [x][3] gets the x^th object
        code_dict = a_store.get_detail_record(ars[0]._detail_objects[1][3].key).data

        # check the code results
        assert(code_dict['text/markdown'][101:109] == 'y("knitr')

        # check part of an image
        imgdata = a_store.get_detail_record(ars[1]._detail_objects[1][3].key).data['image/png'][0:20]
        assert(imgdata == '/9j/4AAQSkZJRgABAQAA')

    def test_multiplecells(self, redis_client, mock_labbook):
        """Make sure that RStudio detects and splits cells"""

        server_monitor = RStudioServerMonitor("test", "test", mock_labbook[2].name,
                                            "foo:activity_monitor:73467b78", config_file=mock_labbook[0])

        mitmlog = open(f"{os.path.dirname(os.path.realpath(__file__))}/73467b78.rserver.dump", "rb")

        # Read activity and return an aggregated activity record
        server_monitor.process_activity(mitmlog)
        # call processor
        server_monitor.store_record() 

        a_store = ActivityStore(mock_labbook[2])
        ars = a_store.get_activity_records()

        # details object [x][3] gets the x^th object
        cell_1 = a_store.get_detail_record(ars[0]._detail_objects[2][3].key).data
        cell_2 = a_store.get_detail_record(ars[0]._detail_objects[3][3].key).data

        # if the cells were divided, there will be two records
        assert(cell_1['text/plain'][55:58] == 'pop')
        assert(cell_2['text/plain'][200:204] == 'stan')
