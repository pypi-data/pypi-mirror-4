import unittest
from pyramid import testing

from pyramid_selectable_renderer import SelectableRendererSetup 
from pyramid_selectable_renderer.custom import RecieveTemplatePathFormat
from pyramid_selectable_renderer.custom import SelectByRetvalLeftGen

dead_or_alive = SelectableRendererSetup(
    RecieveTemplatePathFormat,
    SelectByRetvalLeftGen.generate(lambda x : x),
    renderer_name = "dead_or_alive")

class SelectableRendererIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def setup_view(self):
        def dummy_view(request):
            return request.matchdict["status"], {"name": request.matchdict["name"]}

        renderer = dead_or_alive("pyramid_selectable_renderer:%s.mako")
        self.config.add_view(dummy_view, name="dummy", renderer=renderer)

        def call_view(matchdict):
            from pyramid.view import render_view_to_response
            request = testing.DummyRequest(matchdict=matchdict)
            context = None
            return render_view_to_response(context, request, name="dummy")
        return call_view

        
    def test_render_result(self):
        dead_or_alive.register_to(self.config)
        call_view = self.setup_view()

        result = call_view(dict(name="foo", status="alive"))
        self.assertEquals(result.content_type, "text/html")
        self.assertEquals(result.body, "alive: foo\n")

        result = call_view(dict(name="foo", status="dead"))
        self.assertEquals(result.content_type, "text/html")
        self.assertEquals(result.body, "dead: foo\n")


    def test_BeforeRenderer_Event_call_times(self):
        dead_or_alive.register_to(self.config)
        call_view = self.setup_view()

        counter = [0]
        def count_event(event):
            counter[0] += 1

        from pyramid.events import BeforeRender
        self.config.add_subscriber(count_event, BeforeRender)

        self.assertEquals(counter[0], 0)
        call_view(dict(name="foo", status="dead"))
        self.assertEquals(counter[0], 1)
        call_view(dict(name="foo", status="alive"))
        self.assertEquals(counter[0], 2)

    def test_with_2views(self):
        dead_or_alive.register_to(self.config)

        first_view = self.setup_view()
        result = first_view(dict(name="foo", status="alive"))
        self.assertEquals(result.content_type, "text/html")
        self.assertEquals(result.body, "alive: foo\n")
        

        class DummyForm:
            status = True
            @classmethod
            def validate(cls):
                return cls.status

        def second_view(request):
            status = DummyForm.validate()
            direction =  "alive" if status else "dead"
            return direction, {"name": request.matchdict["name"]}

        renderer = dead_or_alive("pyramid_selectable_renderer:%s.mako")
        self.config.add_view(second_view, name="second", renderer=renderer)

        def call_second_view(name, status=True):
            DummyForm.status = status

            from pyramid.view import render_view_to_response
            request = testing.DummyRequest(matchdict=dict(name=name))
            context = None
            return render_view_to_response(context, request, name="second")

        result = call_second_view("foo", status=True)
        self.assertEquals(result.content_type, "text/html")
        self.assertEquals(result.body, "alive: foo\n")

        result = call_second_view("boo", status=False)
        self.assertEquals(result.content_type, "text/html")
        self.assertEquals(result.body, "dead: boo\n")
        


    #todo refactoring
    def test_2kinds_selectable_renderer_settings(self):
        dead_or_alive.register_to(self.config)
        call_view = self.setup_view()

        result = call_view(dict(name="foo", status="alive"))
        self.assertEquals(result.content_type, "text/html")
        self.assertEquals(result.body, "alive: foo\n")

        ## add another kind selectable renderer

        from pyramid_selectable_renderer.custom import RecieveTemplatePathCandidatesDict
        from pyramid_selectable_renderer.custom import SelectByRequestGen

        dispatch_by_host = SelectableRendererSetup(
            RecieveTemplatePathCandidatesDict,
            SelectByRequestGen.generate(lambda request : request.host),
            renderer_name = "dispatch_by_host")
        
        def dummy_view(request):
            return {"name": request.matchdict["name"]}

        renderer = dispatch_by_host({
                "Asite.com": "pyramid_selectable_renderer:alive.mako",
                "Bsite.com": "pyramid_selectable_renderer:dead.mako",
                })
        self.config.add_view(dummy_view, name="dispatch_by_host", renderer=renderer)

        def call_view(name, host=None):
            from pyramid.view import render_view_to_response
            request = testing.DummyRequest(host=host,matchdict=dict(name=name))
            context = None
            return render_view_to_response(context, request, name="dispatch_by_host")

        
        dispatch_by_host.register_to(self.config)

        result = call_view("foo", host="Asite.com")
        self.assertEquals(result.content_type, "text/html")
        self.assertEquals(result.body, "alive: foo\n")

        result = call_view("boo", host="Bsite.com")
        self.assertEquals(result.content_type, "text/html")
        self.assertEquals(result.body, "dead: boo\n")

if __name__ == "__main__":
    unittest.main()
