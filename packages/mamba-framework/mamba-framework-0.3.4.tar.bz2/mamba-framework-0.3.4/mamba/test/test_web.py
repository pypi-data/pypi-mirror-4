
# Copyright (c) 2012 - Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
Tests for mamba.web
"""

import sys
import tempfile
from os import sep
from cStringIO import StringIO

from twisted.internet import defer
from twisted.trial import unittest
from twisted.python import filepath
from twisted.web.server import Request
from twisted.web.http_headers import Headers
from twisted.web.test.test_web import DummyRequest
from twisted.internet.error import ProcessTerminated
from doublex import Stub, ProxySpy, Spy, called, assert_that

from mamba.core import GNU_LINUX
from mamba.application import appstyles, controller, scripts
from mamba.application import route as decoroute
from mamba.web import stylesheet, page, asyncjson, response, script
from mamba.web.routing import Route, Router, RouteDispatcher

from mamba.test.test_less import less_file
from mamba.test.dummy_app.application.controller.dummy import DummyController


class StylesheetTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        self.doCleanups()
        self.flushLoggedErrors(ProcessTerminated)

    def test_stylesheet_raises_on_not_existent_file(self):

        self.assertRaises(
            stylesheet.FileDontExists,
            stylesheet.Stylesheet,
            'i_dont_exists'
        )

    def test_stylesheet_raises_on_invalid_file_extension(self):

        self.assertRaises(
            stylesheet.InvalidFileExtension,
            stylesheet.Stylesheet,
            '../mamba/test/dummy_app/application/controller/dummy.py'
        )

    def test_stylesheet_raises_on_invalid_file_content(self):

        tmpdir = tempfile.gettempdir()
        fp = filepath.FilePath('{}/test.css'.format(tmpdir))
        fd = fp.open('w')
        fd.write(less_file)
        fd.close()

        self.assertRaises(
            stylesheet.InvalidFile,
            stylesheet.Stylesheet,
            tmpdir + sep + 'test.css'
        )

        fp.remove()

    def test_stylesheet_load_valid_file(self):

        style = stylesheet.Stylesheet(
            '../mamba/test/dummy_app/application/view/stylesheets/dummy.less'
        )

        self.assertTrue(style.data != '')
        self.assertEqual(style.name, 'dummy.less')


class StylesheetManagerTest(unittest.TestCase):

    def setUp(self):
        self.mgr = appstyles.AppStyles()

        if GNU_LINUX:
            self.addCleanup(self.mgr.notifier.loseConnection)

    def tearDown(self):
        self.flushLoggedErrors()

    def load_style(self):
        self.mgr.load(
            '../mamba/test/dummy_app/application/view/stylesheets/dummy.less')

    def test_setup_doesnt_works_until_correct_path(self):
        self.mgr.setup()
        self.assertFalse(len(self.mgr._stylesheets))

        self.mgr._styles_store = (
            '../mamba/test/dummy_app/application/view/stylesheets')

        self.mgr.setup()
        self.assertTrue(len(self.mgr._stylesheets))

    def test_load(self):
        self.load_style()

        self.assertTrue(len(self.mgr._stylesheets))

    def test_loaded_style_is_stylesheet_object(self):
        self.load_style()

        self.assertIsInstance(
            self.mgr.stylesheets['dummy.less'],
            stylesheet.Stylesheet
        )

    def test_reload_just_pass(self):
        self.load_style()
        self.mgr.reload('dummy.less')

    def test_lookup_returns_none_on_unknown_syles(self):
        self.assertEqual(self.mgr.lookup('unknown'), None)

    def test_lookup_returns_an_style_object(self):
        self.load_style()
        self.assertIsInstance(
            self.mgr.lookup('dummy.less'),
            stylesheet.Stylesheet
        )


class ScriptTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        self.doCleanups()
        self.flushLoggedErrors(ProcessTerminated)

    def test_script_raises_on_not_existent_file(self):

        self.assertRaises(
            script.FileDontExists,
            script.Script,
            'i_dont_exists'
        )

    def test_script_raises_on_invalid_file_extension(self):

        self.assertRaises(
            script.InvalidFileExtension,
            script.Script,
            '../mamba/test/dummy_app/application/controller/dummy.py'
        )

    def test_script_raises_on_invalid_file_content(self):

        tmpdir = tempfile.gettempdir()
        fp = filepath.FilePath('{}/test.js'.format(tmpdir))
        fd = fp.open('w')
        fd.write(
            '/* -*- mamba-file-type: mamba-javascript */\n'
            'function dummy() { console.debug(\'dummy_test\'); }'
        )
        fd.close()

        self.assertRaises(
            script.InvalidFile,
            script.Script,
            tmpdir + sep + 'test.js'
        )

        fp.remove()

    def test_script_load_valid_file(self):

        js = script.Script(
            '../mamba/test/dummy_app/application/view/scripts/dummy.js'
        )

        self.assertTrue(js.data != '')
        self.assertEqual(js.name, 'dummy.js')


class ScriptManagerTest(unittest.TestCase):

    def setUp(self):
        self.mgr = scripts.Scripts()

        if GNU_LINUX:
            self.addCleanup(self.mgr.notifier.loseConnection)

    def tearDown(self):
        self.flushLoggedErrors()

    def load_script(self):
        self.mgr.load(
            '../mamba/test/dummy_app/application/view/scripts/dummy.js')

    def test_setup_doesnt_works_until_correct_path(self):
        self.mgr.setup()
        self.assertFalse(len(self.mgr._scripts))

        self.mgr._scripts_store = (
            '../mamba/test/dummy_app/application/view/scripts')

        self.mgr.setup()
        self.assertTrue(len(self.mgr._scripts))

    def test_load(self):
        self.load_script()

        self.assertTrue(len(self.mgr._scripts))

    def test_loaded_script_is_script_object(self):
        self.load_script()

        self.assertIsInstance(
            self.mgr.scripts['dummy.js'],
            script.Script
        )

    # def test_reload_just_pass(self):
    #     self.load_script()
    #     self.mgr.reload('dummy.js')

    def test_lookup_returns_none_on_unknown_scripts(self):
        self.assertEqual(self.mgr.lookup('unknown'), None)

    def test_lookup_returns_an_script_object(self):
        self.load_script()
        self.assertIsInstance(
            self.mgr.lookup('dummy.js'),
            script.Script
        )


class AsyncJSONTest(unittest.TestCase):

    @defer.inlineCallbacks
    def test_asyncjson(self):

        consumer = Spy(Request)

        ajson = ProxySpy(asyncjson.AsyncJSON({'id': 1, 'name': 'Test'}))
        r = yield ajson.begin(consumer)
        for p in r:
            pass
        assert_that(consumer.registerProducer, called().times(1))
        assert_that(consumer.write, called())
        assert_that(consumer.unregisterProducer, called().times(1))
        assert_that(ajson.begin, called())
        self.flushLoggedErrors()


class PageTest(unittest.TestCase):

    def setUp(self):
        self.root = page.Page(self.get_commons())
        if GNU_LINUX:
            self.addCleanup(self.root._styles_manager.notifier.loseConnection)
            self.addCleanup(self.root._scripts_manager.notifier.loseConnection)

    def tearDown(self):
        self.flushLoggedErrors()

    def get_commons(self):

        with Stub() as app:
            app.name = 'Testing App'
            app.language = 'en_EN'
            app.description = 'Test Description'
            app.log_file = 'application.log'

            with Stub() as controllers:
                controllers.get_controllers().returns({})

            with Stub() as styles:
                styles.get_styles().returns({})

            with Stub() as scripts:
                scripts.get_scripts().returns({})

            app.managers = {
                'controller': controllers,
            }

        return app

    def test_page_get_child_return_itself_if_postpath_is_index(self):

        self.assertIdentical(
            self.root,
            self.root.getChild('index', DummyRequest(['']))
        )

    def test_page_get_child_return_itself_if_postpath_is_valid_template(self):

        self.assertIdentical(
            self.root,
            self.root.getChild('test', DummyRequest(['']))
        )

    def test_page_get_child_return_itself_if_postpath_is_missing(self):

        self.assertIdentical(
            self.root,
            self.root.getChild('', DummyRequest(['']))
        )

    def test_page_get_child_returns_registered_childs(self):

        child = DummyController()
        if GNU_LINUX:
            self.addCleanup(child._styles_manager.notifier.loseConnection)
            self.addCleanup(child._scripts_manager.notifier.loseConnection)

        self.root.putChild('dummy', child)

        self.assertIdentical(
            child,
            self.root.getChildWithDefault('dummy', DummyRequest(['']))
        )

    def test_render_get_a_rendered_template(self):

        request = DummyRequest([''])
        request.prepath = ['test']
        self.assertEqual(
            self.root.render_GET(request),
            '<!DOCTYPE html>\n'
            '<html lang="en">\n'
            '<head>\n'
            '    <title></title>\n'
            '</head>\n'
            '<body>\n'
            '    \n'
            '</body>\n'
            '</html>'
        )

    def test_concrete_template_hidden_controller(self):

        child = DummyController()
        if GNU_LINUX:
            self.addCleanup(child._styles_manager.notifier.loseConnection)
            self.addCleanup(child._scripts_manager.notifier.loseConnection)

        self.root.putChild('test', child)

        self.assertIdentical(
            self.root,
            self.root.getChild('test', DummyRequest(['']))
        )

    def test_page_add_script(self):

        style = stylesheet.Stylesheet(
            '../mamba/test/dummy_app/application/view/stylesheets/dummy.less'
        )
        self.root.add_script(style)

        self.assertEqual(
            self.root.getChildWithDefault(
                style.prefix, DummyRequest([''])).basename(),
            style.name
        )

    def test_page_register_controllers(self):

        mgr = controller.ControllerManager()
        if GNU_LINUX:
            self.addCleanup(mgr.notifier.loseConnection)

        sys.path.append('../mamba/test/dummy_app')
        mgr.load('../mamba/test/dummy_app/application/controller/dummy.py')

        if GNU_LINUX:
            for c in mgr.get_controllers().values():
                object = c['object']
                self.addCleanup(object._styles_manager.notifier.loseConnection)
                self.addCleanup(
                    object._scripts_manager.notifier.loseConnection
                )

        self.root._controllers_manager = mgr
        self.root.register_controllers()

        self.assertIdentical(
            self.root.getChildWithDefault('dummy', DummyRequest([''])),
            mgr.lookup('dummy')['object']
        )


class RouteTest(unittest.TestCase):

    def test_compile(self):
        route = Route('GET', '/test', lambda ignore: 'Test Done')
        route.compile()
        self.assertEqual(route.match.pattern, '^/test$')
        route.url = '/test/<int:userId>'
        route.compile()
        self.assertEqual(route.match.pattern, '^/test/(?P<userId>\\d+)$')
        route.url = '/test/<float:userId>'
        route.compile()
        self.assertEqual(
            route.match.pattern, '^/test/(?P<userId>\\d+.?\\d*)$'
        )
        route.url = '/test/<userName>'
        route.compile()
        self.assertEqual(route.match.pattern, '^/test/(?P<userName>([^/]+))$')

    def test_validate(self):
        route = Route('GET', '/test/<int:uderId>', lambda ignore: 'Test Done')
        route.compile()

        with Stub() as dispatcher:
            dispatcher.url = '/test/102'

        self.assertEqual(route.validate(dispatcher), route)

        with Stub() as dispatcher:
            dispatcher.url = '/test'

        self.assertEqual(route.validate(dispatcher), None)

    def test__call__(self):

        controller = Collaborator()
        route = controller.callback.route
        route.compile()

        with Stub() as dispatcher:
            dispatcher.url = '/test/102/10.1/test'

        r = route.validate(dispatcher)
        self.assertEqual(r(controller, None), 'User 102 10.1 test')


class RouterTest(unittest.TestCase):

    def tearDown(self):
        self.flushLoggedErrors()

    @defer.inlineCallbacks
    def test_dispatch_route(self):

        controller = StubController()
        request = request_generator(['/test/102'])

        result = yield controller.render(request)
        self.assertIsInstance(result, response.Ok)
        self.assertEqual(result.subject, 'User ID : 102')
        self.assertEqual(result.headers.get('content-type'), 'text/plain')

    @defer.inlineCallbacks
    def test_dispatch_route_not_found(self):

        controller = StubController()
        request = DummyRequest(['/unknown'])

        result = yield controller.render(request)
        self.assertIsInstance(result, response.NotFound)

    @defer.inlineCallbacks
    def test_dispatch_route_internal_server_error(self):

        controller = StubController()
        request = request_generator(['/test/102'], headers=False)

        result = yield controller.render(request)
        self.assertIsInstance(result, response.InternalServerError)
        self.flushLoggedErrors(AttributeError)

    @defer.inlineCallbacks
    def test_dispatch_route_bad_request(self):

        controller = StubController()
        request = Spy()

        result = yield controller.render(request)
        self.assertIsInstance(result, response.BadRequest)

    @defer.inlineCallbacks
    def test_dispatch_route_not_implemented(self):

        controller = StubController()
        request = request_generator(['/test/102'], 'POST')

        result = yield controller.render(request)
        self.assertIsInstance(result, response.NotImplemented)

    @defer.inlineCallbacks
    def test_dispatch_route_reurns_text_plain_on_txt_returning_route(self):

        StubController.test2 = routes_generator('Plain Text')
        request = request_generator(['/test2'])

        result = yield StubController().render(request)
        self.assertIsInstance(result, response.Ok)
        self.assertEqual(result.subject, 'Plain Text')
        self.assertEqual(result.headers, {'content-type': 'text/plain'})

    @defer.inlineCallbacks
    def test_dispatch_route_returns_text_html_on_html_resturning_route(self):

        StubController.test2 = routes_generator('<h1>HTML Text</h1>')
        request = request_generator(['/test2'])

        result = yield StubController().render(request)
        self.assertIsInstance(result, response.Ok)
        self.assertEqual(result.subject, '<h1>HTML Text</h1>')
        self.assertEqual(result.headers, {'content-type': 'text/html'})

    @defer.inlineCallbacks
    def test_defer_routing_methods(self):

        request = request_generator(['/defer'])
        result = yield StubController().render(request)
        self.assertEqual(result.subject, 'Hello Defer!')

    @defer.inlineCallbacks
    def test_dispatch_route_returns_json_on_response_object(self):

        StubController.test2 = routes_generator(
            response.Ok(
                subject=Person(),
                headers={'content-type': 'application/json'}
            )
        )
        request = request_generator(['/test2'])

        result = yield StubController().render(request)
        self.assertIsInstance(result, response.Ok)
        self.assertEqual(result.headers, {'content-type': 'application/json'})
        self.assertEqual(result.subject, {
            'name': 'Person', 'interests': 'Testing', 'age': 30
        })

    @defer.inlineCallbacks
    def test_dispatch_route_returns_json_on_any_object(self):

        StubController.test2 = routes_generator(Person())

        request = request_generator(['/test2'])

        result = yield StubController().render(request)
        self.assertIsInstance(result, response.Ok)
        self.assertEqual(result.headers, {'content-type': 'application/json'})
        self.assertEqual(result.subject, {
            'name': 'Person', 'interests': 'Testing', 'age': 30
        })

    @defer.inlineCallbacks
    def test_dispatch_route_adds_json_parameters_on_put_or_post_request(self):

        StubController.test2 = routes_generator('Test', method='PUT')
        request = request_generator(['/test2'], method='PUT')
        request.content.write('{"name": "test"}')
        request.content.seek(0, 0)
        request.requestHeaders.setRawHeaders(
            'content-type', ['application/json']
        )

        controller = StubController()

        result = yield controller.render(request)
        self.assertIsInstance(result, response.Ok)
        self.assertTrue('name' in controller.test2.route.callback_args)

    @defer.inlineCallbacks
    def test_dispatch_route_adds_form_parameters_on_put_request(self):

        StubController.test2 = routes_generator('Test', method='PUT')
        request = request_generator(['/test2'], method='PUT')
        request.requestHeaders.setRawHeaders(
            'content-type', ['application/x-www-form-urlencoded']
        )
        request.content.write('name=test')
        request.content.seek(0, 0)
        controller = StubController()

        result = yield controller.render(request)
        self.assertIsInstance(result, response.Ok)
        self.assertTrue('name' in controller.test2.route.callback_args)

    def test_install_routes_register_route(self):

        router = Router()
        router.install_routes(StubController())

        self.assertTrue(len(router.routes['GET']) == 2)

        del router
        router = Router()

        @decoroute('/another_test')
        def another_test(self, request, **kwargs):
            return None

        StubController.another_test = another_test
        router.install_routes(StubController())

        self.assertTrue(len(router.routes['GET']) == 3)

    def test_install_router_fails_when_give_wrong_arguments(self):

        router = Router()

        @decoroute('/test')
        def test(self, request, user_id, **kwargs):
            return 'I will fail'

        StubController.test2 = test
        router.install_routes(StubController())

        # only one of the routes should be installed
        self.assertTrue(len(router.routes['GET']) == 2)


class TestRouteDispatcher(unittest.TestCase):

    def test_sanitize_urls_on_initialization(self):

        route_dispatcher = RouteDispatcher(
            Router(), StubController(), DummyRequest(['////test///one///'])
        )
        self.assertEqual(route_dispatcher.url, '/test/one')

    def test_lookup_returns_route(self):

        controller = StubController()
        request = request_generator(['/test/102'])
        router = Router()
        router.install_routes(controller)
        route_dispatcher = RouteDispatcher(router, controller, request)

        self.assertIsInstance(route_dispatcher.lookup(), Route)

    def test_lookup_returns_none_on_invalid_controller_or_router(self):

        route_dispatcher = RouteDispatcher(
            Router(), StubController(), DummyRequest(['/test'])
        )

        self.assertEqual(route_dispatcher.lookup(), None)

    def test_lookup_returns_not_implemented_on_valid_url_invalid_method(self):

        controller = StubController()
        request = request_generator(['/test/102'], method='POST')
        router = Router()
        router.install_routes(controller)
        route_dispatcher = RouteDispatcher(router, controller, request)

        self.assertEqual(route_dispatcher.lookup(), 'NotImplemented')


class Collaborator(object):

    @decoroute('/test/<int:user_id>/<float:arg2>/<text>')
    def callback(self, request, user_id, arg2, text, **kwargs):
        return 'User {} {} {}'.format(user_id, arg2, text)


class StubController(object):

    def __init__(self):
        self.path = ''
        self._router = Router()
        self._router.install_routes(self)

    def render(self, request):
        return self._router.dispatch(self, request)

    def get_register_path(self):
        return self.path

    @decoroute('/test/<int:user_id>')
    def test(self, request, user_id, **kwargs):
        return 'User ID : {}'.format(user_id)

    @decoroute('/defer')
    @defer.inlineCallbacks
    def deferred(self, request, **kwargs):
        val1 = yield 'Hello '
        val2 = yield 'Defer!'
        defer.returnValue(val1 + val2)


def routes_generator(retval, method='GET'):

    @decoroute('/test2', method=method)
    def test2(self, request, **wkargs):
        return retval

    return test2


def request_generator(url, method='GET', content=True, headers=True):
    request = DummyRequest(url)
    request.method = method
    if content:
        request.content = StringIO()
    if headers:
        request.requestHeaders = Headers()

    return request


class Person(object):
    name = 'Person'
    interests = 'Testing'
    age = 30
