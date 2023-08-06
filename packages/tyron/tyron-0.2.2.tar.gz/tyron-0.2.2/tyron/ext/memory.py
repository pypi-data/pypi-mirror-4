from flask import Blueprint
from flask import send_file
import inspect as pyinspect
import objgraph
import tempfile

inspect = Blueprint('objgraph', __name__)


def graph_refs(refs):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    objgraph.show_refs(
        [refs],
        refcounts=True,
        filename=tmp.name
    )
    return send_file(tmp, mimetype='image/png')

@inspect.route('/subscriptions/')
def subscriptions():
    from tyron import tyron
    return graph_refs(tyron.subscriptions)

@inspect.route('/application/')
def application():
    from tyron import tyron
    return graph_refs(tyron.application)

@inspect.route('/growth/')
def growth():
    objgraph.show_growth(limit=10)
    return ''

@inspect.route('/common/')
def common():
    objgraph.show_most_common_types()
    return ''

@inspect.route('/gc/')
def run_gc():
    import gc
    objgraph.show_growth(limit=10)
    gc.collect()
    objgraph.show_growth(limit=10)
    return ''

@inspect.route('/leaking/')
def leaking():
    from tyron import tyron
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    objgraph.show_backrefs(
        [tyron.subscriptions], filename=tmp.name
    )
    return send_file(tmp, mimetype='image/png')