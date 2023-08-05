from speedrack import app

from flask import url_for

from nose.tools import *

class TestRoutes(object):
    client = app.test_client()

    def check_route(self, expected, route):
        assert_equal(expected, url_for(route))

    def test_routes(self):
        tests = [
            ("/", "show_tasks"),
            ("/config/clear", "clear_config"),
            ("/config/reload", "reload_config"),
            ("/debug", "show_debug"),
            ("/toggle_inactive", "toggle_inactive_tasks"),
            ("/help", "show_help"),
        ]
        with app.test_request_context():
            for (expected, route) in tests:
                yield self.check_route, expected, route


# import mock
# from test.helpers import *
# from speedrack.models import TaskList, Task
# class TestTaskViews(object):
#     client = app.test_client()

    # def setup(self):
    #     self.gene = Factory(Gene)

    # def test_task_list(self):
        # with app.test_request_context():
        #     response = self.client.get(url_for("show_tasks"))
        #     print response
        #     raise

    # def test_show_gene_with_locus(self):
    #     with mock.patch.object(Gene, 'by_id_or_locus',
    #                            classmethod(lambda *x:self.gene)):
    #         with app.test_request_context():
    #             response = self.client.get(url_for("show_gene",
    #                                          gene_id=self.gene.id))

    #             assert_in(self.gene.locus, response.data)
