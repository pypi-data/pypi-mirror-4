from tg import expose, redirect
from tg.decorators import with_trailing_slash
from pylons import tmpl_context as c

from allura.controllers import repository

class BranchBrowser(repository.BranchBrowser):

    @expose('jinja:forgehg:templates/hg/index.html')
    @with_trailing_slash
    def index(self, limit=None, page=0, count=0, **kw):
        latest = c.app.repo.latest(branch=self._branch)
        if not latest:
            return dict(allow_fork=False, log=[])
        redirect(c.app.repo._impl.url_for_symbolic(latest._id) + 'tree/')
