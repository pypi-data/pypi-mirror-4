class MatchDictFinder(object):
    def __init__(self, model, session_factory, filters):
        self.model = model
        self.filters = filters
        self.session_factory = session_factory

    def __call__(self, request):
        session = self.session_factory()
        q = session.query(self.model)
        for f in self.filters:
            q = q.filter(f[0]==request.matchdict[f[1]])
        return q.one()
