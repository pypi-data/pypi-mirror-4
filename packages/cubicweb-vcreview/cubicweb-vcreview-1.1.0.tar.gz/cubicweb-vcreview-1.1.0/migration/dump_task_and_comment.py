# simple script that make a json dump of task and first level comment on patch
#
# run it through cubicweb-ctl shell BEFORE the update
#
# output is done on stdout. redirect it.


patch_task = '''
Any P, ST, T, D, AST
WHERE P has_activity A,
      P is Patch,
      P in_state S,
      S name ST,
      A title T,
      A description D,
      A in_state AS,
      AS name AST
'''


patch_comment = '''
Any P, ST, C
WHERE CO comments P,
      P in_state S,
      P is Patch,
      S name ST,
      CO content C
'''

vc_task = '''
Any P, ST, RE, LID, T, D, AST
WHERE P patch_revision RE,
      IP point_of RE,
      IP has_activity A,
      IP lid LID,
      P in_state S,
      P is Patch,
      S name ST,
      A title T,
      A description D,
      A in_state AS,
      AS name AST
'''

vc_comment = '''
Any P, ST, RE, LID, C
WHERE P patch_revision RE,
      IP point_of RE,
      CO comments IP,
      IP lid LID,
      P in_state S,
      P is Patch,
      S name ST,
      CO content C
'''

import re
RE_NODE= re.compile('# Node ID ([a-f0-9]{40})')

nodes_cache = {}

def get_node(patch_eid):
    if patch_eid in nodes_cache:
        return nodes_cache[patch_eid]
    vc = session.entity_from_eid(patch_eid)
    match = vc.data
    if match is not None:
        match = RE_NODE.search(match.getvalue())
        if match is not None:
            match = match.group(1)
        nodes_cache[patch_eid] = match
    return match

data = {}

for patch, state, title, comment, tstate in rql(patch_task):
    patch_key = (patch, state)
    patch_data = data.setdefault(patch_key, [])
    acti_data = {'type': 'task',
                 'title': title,
                 'comment': comment,
                 'state': tstate}
    patch_data.append((None, None, acti_data))

for patch, state, comment in rql(patch_comment):
    patch_key = (patch, state)
    patch_data = data.setdefault(patch_key, [])
    acti_data = {'type': 'comment',
                 'comment': comment,}
    patch_data.append((None, None, acti_data))

for patch, state, vc, lid, title, comment, tstate in rql(vc_task):
    patch_key = (patch, state)
    patch_data = data.setdefault(patch_key, [])
    acti_data = {'type': 'task',
                 'title': title,
                 'comment': comment,
                 'state': tstate}
    patch_data.append((get_node(vc), None, acti_data))

for patch, state, vc, lid, comment in rql(vc_comment):
    patch_key = (patch, state)
    patch_data = data.setdefault(patch_key, [])
    acti_data = {'type': 'comment',
                 'comment': comment,
                }
    patch_data.append((get_node(vc), None, acti_data))

import json
print json.dumps(data.items(), indent=4)
