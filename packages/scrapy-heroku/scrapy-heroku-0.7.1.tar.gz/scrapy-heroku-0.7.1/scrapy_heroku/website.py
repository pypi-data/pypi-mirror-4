from datetime import datetime

from twisted.web import resource, static
from twisted.application.service import IServiceCollection

from scrapy.utils.misc import load_object

from .interfaces import IPoller, IEggStorage, ISpiderScheduler

from . import webservice


class Processes(resource.Resource):
    def __init__(self, root):
        resource.Resource.__init__(self)
        self.root = root

    def render_GET(self, txrequest):
        vars = {
            'projects': ', '.join(self.root.scheduler.list_projects()),
        }
        return """
<html>
<head><title>Scrapyd</title></head>
<body>
<h1>Scrapyd</h1>
<p>Available projects: <b>%(projects)s</b></p>
<ul>
<li><a href="/jobs">Jobs</a></li>
<li><a href="/items/">Items</li>
<li><a href="/logs/">Logs</li>
<li><a href="http://doc.scrapy.org/en/latest/topics/scrapyd.html">Documentation</a></li>
</ul>

<h2>How to schedule a spider?</h2>

<p>To schedule a spider you need to use the API (this web UI is only for
monitoring)</p>

<p>Example using <a href="http://curl.haxx.se/">curl</a>:</p>
<p><code>curl http://localhost:6800/schedule.json -d project=default -d spider=somespider</code></p>

<p>For more information about the API, see the <a href="http://doc.scrapy.org/en/latest/topics/scrapyd.html">Scrapyd documentation</a></p>
</body>
</html>
""" % vars
