# coding: utf-8
import unittest
from nose.tools import raises

from python_rest_handler import *


class Model(object):
    pass

class DM(DataManager):
    pass


class ManualInheritanceTests(unittest.TestCase):
    def test_valid_request_handler_instance_receive_a_rest_handler_attribute(self):
        class CustomHandler(RestRequestHandler):
            model = Model
            data_manager = DM
        handler = CustomHandler()
        self.assertEquals(RestHandler, handler.rest_handler.__class__)

    def test_valid_request_handler_instance_receive_default_attributes(self):
        class CustomHandler(RestRequestHandler):
            model = Model
            data_manager = DM
        handler = CustomHandler()
        self.assertEquals('model/', handler.template_path)
        self.assertEquals('list.html', handler.list_template)
        self.assertEquals('edit.html', handler.edit_template)
        self.assertEquals('show.html', handler.show_template)
        self.assertEquals('/', handler.redirect_pos_action)
        self.assertEquals(None, handler.extra_attributes)

    def test_valid_request_handler_instance_create_an_instance_of_its_data_manager(self):
        class CustomHandler(RestRequestHandler):
            model = Model
            data_manager = DM
        handler = CustomHandler()
        self.assertEquals(True, isinstance(handler.data_manager, DM))
        self.assertEquals(handler, handler.data_manager.handler)
        self.assertEquals(Model, handler.data_manager.model)

    def test_two_subclasses_of_a_rest_request_handler_must_not_share_instance_variables(self):
        class Model1(object): pass
        class Model2(object): pass
        class DM1(DataManager): pass
        class DM2(DataManager): pass
        class CustomHandler(RestRequestHandler): pass
        class CustomHandler1(CustomHandler):
            model = Model1
            data_manager = DM1
        class CustomHandler2(CustomHandler):
            model = Model2
            data_manager = DM2
        handler1 = CustomHandler1()
        handler2 = CustomHandler2()
        self.assertEquals(True, handler1.rest_handler != handler2.rest_handler)
        self.assertEquals(DM1, handler1.data_manager.__class__)
        self.assertEquals(DM2, handler2.data_manager.__class__)
        self.assertEquals(Model1, handler1.data_manager.model)
        self.assertEquals(Model2, handler2.data_manager.model)

    @raises(NotImplementedError)
    def test_request_handler_instance_must_raise_an_self_explained_error_if_there_is_no_model(self):
        class CustomHandler(RestRequestHandler):
            data_manager = DM
        CustomHandler()

    @raises(NotImplementedError)
    def test_request_handler_instance_must_raise_an_self_explained_error_if_there_is_no_data_manager(self):
        class CustomHandler(RestRequestHandler):
            model = Model
        CustomHandler()

    def test_use_model_name_to_define_template_path(self):
        class CustomHandler(RestRequestHandler):
            model = Model
            data_manager = DM
        handler = CustomHandler()
        self.assertEquals('model/', handler.__class__.template_path)

    def test_it_can_have_extra_attributes(self):
        class CustomHandler(RestRequestHandler):
            model = Model
            data_manager = DM
            extra_attributes = []
        handler = CustomHandler()
        self.assertEquals([], handler.__class__.extra_attributes)


class RestHandlerTests(unittest.TestCase):
    def test_rest_handler_create_a_valid_rest_request_handler(self):
        class CustomHandler(RestRequestHandler):
            pass
        handler_cls = rest_handler(Model, DM, CustomHandler)
        self.assertEquals(DM, handler_cls.data_manager)
        self.assertEquals(Model, handler_cls.model)

    def test_rest_handler_class_can_be_instantiated(self):
        class CustomHandler(RestRequestHandler):
            pass
        cls = rest_handler(Model, DM, CustomHandler)
        cls()

    def test_rest_handler_create_a_subclass_of_the_handler_class(self):
        class CustomHandler(RestRequestHandler):
            pass
        cls = rest_handler(Model, DM, CustomHandler)
        self.assertEquals(True, isinstance(cls(), CustomHandler))

    @raises(NotImplementedError)
    def test_rest_handler_must_raise_an_self_explained_error_if_there_is_no_data_manager(self):
        class CustomHandler(RestRequestHandler):
            pass
        cls = rest_handler(Model, None, CustomHandler)
        cls()

    def test_rest_handler_must_set_default_attributes(self):
        class CustomHandler(RestRequestHandler):
            pass
        cls = rest_handler(Model, DM, CustomHandler)
        self.assertEquals('model/', cls.template_path)
        self.assertEquals('list.html', cls.list_template)
        self.assertEquals('edit.html', cls.edit_template)
        self.assertEquals('show.html', cls.show_template)
        self.assertEquals('/', cls.redirect_pos_action)
        self.assertEquals(None, cls.extra_attributes)

    def test_rest_handler_can_customize_attributes(self):
        class CustomHandler(RestRequestHandler):
            pass
        func = lambda x: x
        cls = rest_handler(Model, DM, CustomHandler, template_path='x/', list_template='list.json',
            edit_template='edit.json', show_template='show.json', redirect_pos_action='/x',
            extra_attributes=[func])
        self.assertEquals('x/', cls.template_path)
        self.assertEquals('list.json', cls.list_template)
        self.assertEquals('edit.json', cls.edit_template)
        self.assertEquals('show.json', cls.show_template)
        self.assertEquals('/x', cls.redirect_pos_action)
        self.assertEquals([func], cls.extra_attributes)

    def test_it_must_add_number_sufix_in_the_class_name_to_avoid_conflict(self):
        class CustomHandler(RestRequestHandler):
            pass
        cls = rest_handler(Model, DM, CustomHandler)
        self.assertEquals('ModelCustomHandler1', cls.__name__)
        cls = rest_handler(Model, DM, CustomHandler)
        self.assertEquals('ModelCustomHandler2', cls.__name__)


class RestRoutesTests(unittest.TestCase):
    def test_rest_routes_created_routes_using_model_name_as_route_prefix(self):
        class CustomHandler(RestRequestHandler):
            pass
        routes = rest_routes(Model, DM, CustomHandler)
        for route in routes:
            route = route[0]
            self.assertEquals(True, route.startswith('/model'))

    def test_prefix_can_be_customized(self):
        class CustomHandler(RestRequestHandler):
            pass
        routes = rest_routes(Model, DM, CustomHandler, prefix='x')
        for route in routes:
            route = route[0]
            self.assertEquals(True, route.startswith('/x'))


class RoutesTests(unittest.TestCase):
    def test_routes(self):
        self.assertEquals([(1, 2), (3, 4)], routes([(1, 2), (3, 4)]))
        self.assertEquals([(1, 2), (3, 4)], routes([[(1, 2), (3, 4)]]))
        self.assertEquals([(1, 2), (5, 6), (7, 8), (3, 4)], routes([(1, 2), [(5, 6), (7, 8)], (3, 4)]))
