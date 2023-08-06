
from docutils import nodes, utils
from docutils.parsers.rst.roles import register_canonical_role, set_classes

def card_reference_role(role, rawtext, text, lineno, inliner,
                       options={}, content=[]):
    text = text.strip()
    try:
        wikiid, rest = text.split(u':', 1)
    except:
        wikiid, rest = text, text
    context = inliner.document.settings.context
    cardrset = context._cw.execute('Card X WHERE X wikiid %(id)s',
                                   {'id': wikiid})
    if cardrset:
        ref = cardrset.get_entity(0, 0).absolute_url()
    else:
        schema = context._cw.vreg.schema
        if schema.eschema('Card').has_perm(context._cw, 'add'):
            ref = context._cw.build_url('view', vid='creation', etype='Card', wikiid=wikiid)
        else:
            ref = '#'
    set_classes(options)
    return [nodes.reference(rawtext, utils.unescape(rest), refuri=ref,
                            **options)], []

register_canonical_role('card', card_reference_role)
