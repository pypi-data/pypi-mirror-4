"""

    routr.app -- basic WSGI app as a shortcut for using routr
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

__all__ = ('App',)

class App(object):

    def __init__(self, ):
        self.config = config
        self.routes = self.make_routes()

    def wcat(self, id):
        if not ":" in id:
            raise HTTPNotFound()
        ctype, uri = id.split(":", 1)
        task = Task(uri, ctype)
        try:
            processor = self.config.processors[task.ctype]
        except KeyError:
            raise HTTPNotFound()
        (new_tasks, finished_task) = processor.process(task)
        store_task(finished_task)
        q = runtime.queue()
        for t in new_tasks:
            q.put(json_dumps(t))
        return processor.render(finished_task.struct)

    def make_routes(self):
        return route(
            GET('/{id:path}', self.wcat),
            )

    def __call__(self, environ, start_response):
        request = Request(environ)
        with runtime.new(self.config):
            try:
                trace = self.routes(request)
                args = inject_args(trace.target, trace.args,
                    request=request)

                response = trace.target(*args, **trace.kwargs)

            except NoMatchFound as e:
                response = e.response
            except HTTPError as e:
                response = e

            if not isinstance(response, Response):
                response = Response(json=response)

            return response(environ, start_response)
