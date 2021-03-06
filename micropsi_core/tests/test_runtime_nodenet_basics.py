#!/usr/local/bin/python
# -*- coding: utf-8 -*-

"""

"""
import os
from micropsi_core import runtime
from micropsi_core import runtime as micropsi
import mock
import pytest

__author__ = 'joscha'
__date__ = '29.10.12'


def test_new_nodenet(test_nodenet, resourcepath, engine):
    success, nodenet_uid = micropsi.new_nodenet("Test_Nodenet", engine=engine, worldadapter="Default", owner="tester")
    assert success
    assert nodenet_uid != test_nodenet
    assert micropsi.get_available_nodenets("tester")[nodenet_uid].name == "Test_Nodenet"
    n_path = os.path.join(resourcepath, runtime.NODENET_DIRECTORY, nodenet_uid + ".json")
    assert os.path.exists(n_path)

    # get_available_nodenets
    nodenets = micropsi.get_available_nodenets()
    mynets = micropsi.get_available_nodenets("tester")
    assert test_nodenet in nodenets
    assert nodenet_uid in nodenets
    assert nodenet_uid in mynets
    assert test_nodenet not in mynets

    # delete_nodenet
    micropsi.delete_nodenet(nodenet_uid)
    assert nodenet_uid not in micropsi.get_available_nodenets()
    assert not os.path.exists(n_path)


def test_nodenet_data_gate_parameters(fixed_nodenet):
    from micropsi_core.nodenet.node import Nodetype
    data = micropsi.nodenets[fixed_nodenet].get_data()
    assert data['nodes']['n0005']['gate_parameters'] == {}
    micropsi.set_gate_parameters(fixed_nodenet, 'n0005', 'gen', {'threshold': 1})
    data = micropsi.nodenets[fixed_nodenet].get_data()
    assert data['nodes']['n0005']['gate_parameters'] == {'gen': {'threshold': 1}}
    defaults = Nodetype.GATE_DEFAULTS.copy()
    defaults.update({'threshold': 1})
    data = micropsi.nodenets[fixed_nodenet].get_node('n0005').get_data()['gate_parameters']
    assert data == {'gen': {'threshold': 1}}


def test_user_prompt(fixed_nodenet, resourcepath):
    import os
    nodetype_file = os.path.join(resourcepath, 'Test', 'nodetypes.json')
    nodefunc_file = os.path.join(resourcepath, 'Test', 'nodefunctions.py')
    with open(nodetype_file, 'w') as fp:
        fp.write('{"Testnode": {\
            "name": "Testnode",\
            "slottypes": ["gen", "foo", "bar"],\
            "gatetypes": ["gen", "foo", "bar"],\
            "nodefunction_name": "testnodefunc",\
            "parameters": ["testparam"],\
            "parameter_defaults": {\
                "testparam": 13\
              }\
            }}')
    with open(nodefunc_file, 'w') as fp:
        fp.write("def testnodefunc(netapi, node=None, **prams):\r\n    return 17")

    micropsi.reload_native_modules()
    res, uid = micropsi.add_node(fixed_nodenet, "Testnode", [10, 10], name="Test")
    nativemodule = micropsi.nodenets[fixed_nodenet].get_node(uid)

    options = [{'key': 'foo_parameter', 'label': 'Please give value for "foo"', 'values': [23, 42]}]
    micropsi.nodenets[fixed_nodenet].netapi.ask_user_for_parameter(
        nativemodule,
        "foobar",
        options
    )
    result, data = micropsi.get_calculation_state(fixed_nodenet, nodenet={})
    assert 'user_prompt' in data
    assert data['user_prompt']['msg'] == 'foobar'
    assert data['user_prompt']['node']['uid'] == uid
    assert data['user_prompt']['options'] == options
    # response
    micropsi.user_prompt_response(fixed_nodenet, uid, {'foo_parameter': 42}, True)
    assert micropsi.nodenets[fixed_nodenet].get_node(uid).get_parameter('foo_parameter') == 42
    assert micropsi.nodenets[fixed_nodenet].is_active
    from micropsi_core.nodenet import nodefunctions
    tmp = nodefunctions.concept
    nodefunc = mock.Mock()
    nodefunctions.concept = nodefunc
    micropsi.nodenets[fixed_nodenet].step()
    foo = micropsi.nodenets[fixed_nodenet].get_node('n0001').clone_parameters()
    foo.update({'foo_parameter': 42})
    assert nodefunc.called_with(micropsi.nodenets[fixed_nodenet].netapi, micropsi.nodenets[fixed_nodenet].get_node('n0001'), foo)
    micropsi.nodenets[fixed_nodenet].get_node('n0001').clear_parameter('foo_parameter')
    assert micropsi.nodenets[fixed_nodenet].get_node('n0001').get_parameter('foo_parameter') is None
    nodefunctions.concept = tmp


def test_user_notification(test_nodenet, node):
    api = micropsi.nodenets[test_nodenet].netapi
    node_obj = api.get_node(node)
    api.notify_user(node_obj, "Hello there")
    result, data = micropsi.get_calculation_state(test_nodenet, nodenet={'nodespaces': [None]})
    assert 'user_prompt' in data
    assert data['user_prompt']['node']['uid'] == node
    assert data['user_prompt']['msg'] == "Hello there"


def test_nodespace_removal(fixed_nodenet):
    res, uid = micropsi.add_nodespace(fixed_nodenet, [100, 100], nodespace=None, name="testspace")
    res, n1_uid = micropsi.add_node(fixed_nodenet, 'Register', [100, 100], nodespace=uid, name="sub1")
    res, n2_uid = micropsi.add_node(fixed_nodenet, 'Register', [100, 200], nodespace=uid, name="sub2")
    micropsi.add_link(fixed_nodenet, n1_uid, 'gen', n2_uid, 'gen', weight=1, certainty=1)
    res, sub_uid = micropsi.add_nodespace(fixed_nodenet, [100, 100], nodespace=uid, name="subsubspace")
    micropsi.delete_nodespace(fixed_nodenet, uid)
    # assert that the nodespace is gone
    assert not micropsi.nodenets[fixed_nodenet].is_nodespace(uid)
    assert uid not in micropsi.nodenets[fixed_nodenet].get_data()['nodespaces']
    # assert that the nodes it contained are gone
    assert not micropsi.nodenets[fixed_nodenet].is_node(n1_uid)
    assert n1_uid not in micropsi.nodenets[fixed_nodenet].get_data()['nodes']
    assert not micropsi.nodenets[fixed_nodenet].is_node(n2_uid)
    assert n2_uid not in micropsi.nodenets[fixed_nodenet].get_data()['nodes']
    # assert that sub-nodespaces are gone as well
    assert not micropsi.nodenets[fixed_nodenet].is_nodespace(sub_uid)
    assert sub_uid not in micropsi.nodenets[fixed_nodenet].get_data()['nodespaces']


def test_clone_nodes_nolinks(fixed_nodenet):
    nodenet = micropsi.get_nodenet(fixed_nodenet)
    success, result = micropsi.clone_nodes(fixed_nodenet, ['n0001', 'n0002'], 'none', offset=[10, 20, 2])
    assert success
    for n in result.values():
        if n['name'] == 'A1_copy':
            a1_copy = n
        elif n['name'] == 'A2_copy':
            a2_copy = n
    assert nodenet.is_node(a1_copy['uid'])
    assert a1_copy['uid'] != 'n0001'
    assert a1_copy['type'] == nodenet.get_node('n0001').type
    assert a1_copy['parameters'] == nodenet.get_node('n0001').clone_parameters()
    assert a1_copy['position'][0] == nodenet.get_node('n0001').position[0] + 10
    assert a1_copy['position'][1] == nodenet.get_node('n0001').position[1] + 20
    assert a1_copy['position'][2] == nodenet.get_node('n0001').position[2] + 2
    assert nodenet.is_node(a2_copy['uid'])
    assert a2_copy['name'] == nodenet.get_node('n0002').name + '_copy'
    assert a2_copy['uid'] != 'n0002'
    assert len(result.keys()) == 2
    assert a1_copy['links'] == {}
    assert a2_copy['links'] == {}


def test_clone_nodes_all_links(fixed_nodenet):
    nodenet = micropsi.get_nodenet(fixed_nodenet)
    success, result = micropsi.clone_nodes(fixed_nodenet, ['n0001', 'n0002'], 'all')
    assert success
    # expect 3 instead of two results, because the sensor that links to A1 should be delivered
    # as a followupdnode to A1_copy to render incoming links
    assert len(result.keys()) == 3
    for n in result.values():
        if n['name'] == 'A1_copy':
            a1_copy = n
        elif n['name'] == 'A2_copy':
            a2_copy = n

    # assert the link between a1-copy and a2-copy exists
    a1link = a1_copy['links']['por'][0]
    assert a1link['target_node_uid'] == a2_copy['uid']

    # assert the link between sensor and the a1-copy exists
    sensor = nodenet.get_node('n0005').get_data()
    candidate = None
    for link in sensor['links']['gen']:
        if link['target_node_uid'] == a1_copy['uid']:
            candidate = link
    assert candidate['target_slot_name'] == 'gen'


def test_clone_nodes_internal_links(fixed_nodenet):
    nodenet = micropsi.get_nodenet(fixed_nodenet)
    success, result = micropsi.clone_nodes(fixed_nodenet, ['n0001', 'n0002'], 'internal')
    assert success
    assert len(result.keys()) == 2
    for n in result.values():
        if n['name'] == 'A1_copy':
            a1_copy = n
        elif n['name'] == 'A2_copy':
            a2_copy = n

    # assert the link between a1-copy and a2-copy exists
    a1link = a1_copy['links']['por'][0]
    assert a1link['target_node_uid'] == a2_copy['uid']

    # assert the link between sensor and the a1-copy does not exist
    sensor = nodenet.get_node('n0005').get_data()
    candidate = None
    for link in sensor['links']['gen']:
        if link['target_node_uid'] == a1_copy['uid']:
            candidate = link
    assert candidate is None


def test_clone_nodes_to_new_nodespace(fixed_nodenet):
    nodenet = micropsi.get_nodenet(fixed_nodenet)

    res, testspace_uid = micropsi.add_nodespace(fixed_nodenet, [100, 100], nodespace=None, name="testspace")

    success, result = micropsi.clone_nodes(fixed_nodenet, ['n0001', 'n0002'], 'internal', nodespace=testspace_uid)

    assert success
    assert len(result.keys()) == 2
    for n in result.values():
        if n['name'] == 'A1_copy':
            a1_copy = n
        elif n['name'] == 'A2_copy':
            a2_copy = n

    a1_copy = nodenet.get_node(a1_copy['uid'])
    a2_copy = nodenet.get_node(a2_copy['uid'])

    assert a1_copy.parent_nodespace == testspace_uid
    assert a2_copy.parent_nodespace == testspace_uid


def test_clone_nodes_copies_gate_params(fixed_nodenet):
    nodenet = micropsi.get_nodenet(fixed_nodenet)
    micropsi.set_gate_parameters(fixed_nodenet, 'n0001', 'gen', {'maximum': 0.1})
    success, result = micropsi.clone_nodes(fixed_nodenet, ['n0001'], 'internal')
    assert success
    copy = nodenet.get_node(list(result.keys())[0])
    assert round(copy.get_gate_parameters()['gen']['maximum'], 2) == 0.1


def test_modulators(fixed_nodenet, engine):
    nodenet = micropsi.get_nodenet(fixed_nodenet)
    # assert modulators are instantiated from the beginning
    assert nodenet._modulators != {}
    assert nodenet.get_modulator('emo_activation') is not None

    # set a modulator
    nodenet.set_modulator("test_modulator", -1)
    assert nodenet.netapi.get_modulator("test_modulator") == -1

    # assert change_modulator sets diff.
    nodenet.netapi.change_modulator("test_modulator", 0.42)
    assert round(nodenet.netapi.get_modulator("test_modulator"), 4) == -0.58

    # no modulators should be set if we disable the emotional_parameter module
    res, uid = micropsi.new_nodenet('foobar', engine, use_modulators=False)
    new_nodenet = micropsi.get_nodenet(uid)
    assert new_nodenet._modulators == {}
    # and no Emo-stepoperator should be set.
    for item in new_nodenet.stepoperators:
        assert 'Emotional' not in item.__class__.__name__


def test_modulators_sensor_actor_connection(test_nodenet, test_world):
    nodenet = micropsi.get_nodenet(test_nodenet)
    micropsi.set_nodenet_properties(test_nodenet, worldadapter="Braitenberg", world_uid=test_world)
    res, s1_id = micropsi.add_node(test_nodenet, "Sensor", [10, 10], None, name="brightness_l", parameters={'datasource': 'brightness_l'})
    res, s2_id = micropsi.add_node(test_nodenet, "Sensor", [20, 20], None, name="emo_activation", parameters={'datasource': 'emo_activation'})
    res, a1_id = micropsi.add_node(test_nodenet, "Actor", [30, 30], None, name="engine_l", parameters={'datatarget': 'engine_l'})
    res, a2_id = micropsi.add_node(test_nodenet, "Actor", [40, 40], None, name="base_importance_of_intention", parameters={'datatarget': 'base_importance_of_intention'})
    res, r1_id = micropsi.add_node(test_nodenet, "Register", [10, 30], None, name="r1")
    res, r2_id = micropsi.add_node(test_nodenet, "Register", [10, 30], None, name="r2")
    s1 = nodenet.get_node(s1_id)
    s2 = nodenet.get_node(s2_id)
    r1 = nodenet.get_node(r1_id)
    r2 = nodenet.get_node(r2_id)
    s2.set_gate_parameter('gen', 'maximum', 999)
    micropsi.add_link(test_nodenet, r1_id, 'gen', a1_id, 'gen')
    micropsi.add_link(test_nodenet, r2_id, 'gen', a2_id, 'gen')
    r1.activation = 0.3
    r2.activation = 0.7
    emo_val = nodenet.get_modulator("emo_activation")

    # patch reset method, to check if datatarget was written
    def nothing():
        pass
    nodenet.worldadapter_instance.reset_datatargets = nothing

    nodenet.step()
    assert round(nodenet.worldadapter_instance.datatargets['engine_l'], 3) == 0.3
    assert round(s1.activation, 3) == round(nodenet.worldadapter_instance.get_datasource_value('brightness_l'), 3)
    assert round(s2.activation, 3) == round(emo_val, 3)
    assert round(nodenet.get_modulator('base_importance_of_intention'), 3) == 0.7
    assert round(nodenet.worldadapter_instance.datatargets['engine_l'], 3) == 0.3
    emo_val = nodenet.get_modulator("emo_activation")
    nodenet.step()
    assert round(s2.activation, 3) == round(emo_val, 3)


def test_node_parameters(fixed_nodenet, resourcepath):
    import os
    nodetype_file = os.path.join(resourcepath, 'Test', 'nodetypes.json')
    nodefunc_file = os.path.join(resourcepath, 'Test', 'nodefunctions.py')
    with open(nodetype_file, 'w') as fp:
        fp.write('{"Testnode": {\
            "name": "Testnode",\
            "slottypes": ["gen", "foo", "bar"],\
            "gatetypes": ["gen", "foo", "bar"],\
            "nodefunction_name": "testnodefunc",\
            "parameters": ["linktype", "threshold", "protocol_mode"],\
            "parameter_values": {\
                "linktype": ["catexp", "subsur"],\
                "protocol_mode": ["all_active", "most_active_one"]\
            },\
            "parameter_defaults": {\
                "linktype": "catexp",\
                "protocol_mode": "all_active"\
            }}\
        }')
    with open(nodefunc_file, 'w') as fp:
        fp.write("def testnodefunc(netapi, node=None, **prams):\r\n    return 17")

    assert micropsi.reload_native_modules()
    res, uid = micropsi.add_node(fixed_nodenet, "Testnode", [10, 10], name="Test", parameters={"linktype": "catexp", "threshold": "", "protocol_mode": "all_active"})
    # nativemodule = micropsi.nodenets[fixed_nodenet].get_node(uid)
    assert micropsi.save_nodenet(fixed_nodenet)


def test_delete_linked_nodes(fixed_nodenet):

    nodenet = micropsi.get_nodenet(fixed_nodenet)
    netapi = nodenet.netapi

    # create all evil (there will never be another dawn)
    root_of_all_evil = netapi.create_node("Pipe", None)
    evil_one = netapi.create_node("Pipe", None)
    evil_two = netapi.create_node("Pipe", None)

    netapi.link_with_reciprocal(root_of_all_evil, evil_one, "subsur")
    netapi.link_with_reciprocal(root_of_all_evil, evil_two, "subsur")

    for link in evil_one.get_gate("sub").get_links():
        link.source_node.name  # touch of evil
        link.target_node.name  # touch of evil

    for link in evil_two.get_gate("sur").get_links():
        link.source_node.name  # touch of evil
        link.target_node.name  # touch of evil

    # and the name of the horse was death
    netapi.delete_node(root_of_all_evil)
    netapi.delete_node(evil_one)
    netapi.delete_node(evil_two)


def test_multiple_nodenet_interference(engine, resourcepath):
    import os
    nodetype_file = os.path.join(resourcepath, 'Test', 'nodetypes.json')
    nodefunc_file = os.path.join(resourcepath, 'Test', 'nodefunctions.py')
    with open(nodetype_file, 'w') as fp:
        fp.write('{"Testnode": {\
            "name": "Testnode",\
            "slottypes": ["gen", "foo", "bar"],\
            "gatetypes": ["gen", "foo", "bar"],\
            "nodefunction_name": "testnodefunc"\
        }}')
    with open(nodefunc_file, 'w') as fp:
        fp.write("def testnodefunc(netapi, node=None, **prams):\r\n    node.get_gate('gen').gate_function(17)")

    micropsi.reload_native_modules()

    result, n1_uid = micropsi.new_nodenet('Net1', engine=engine, owner='Pytest User')
    result, n2_uid = micropsi.new_nodenet('Net2', engine=engine, owner='Pytest User')

    n1 = micropsi.nodenets[n1_uid]
    n2 = micropsi.nodenets[n2_uid]

    nativemodule = n1.netapi.create_node("Testnode", None, "Testnode")
    register1 = n1.netapi.create_node("Register", None, "Register1")
    n1.netapi.link(nativemodule, 'gen', register1, 'gen', weight=1.2)

    source2 = n2.netapi.create_node("Register", None, "Source2")
    register2 = n2.netapi.create_node("Register", None, "Register2")
    n2.netapi.link(source2, 'gen', source2, 'gen')
    n2.netapi.link(source2, 'gen', register2, 'gen', weight=0.9)
    source2.activation = 0.7

    micropsi.step_nodenet(n2.uid)

    assert n1.current_step == 0
    assert register1.activation == 0
    assert register1.name == "Register1"
    assert nativemodule.name == "Testnode"
    assert round(register1.get_slot('gen').get_links()[0].weight, 2) == 1.2
    assert register1.get_slot('gen').get_links()[0].source_node.name == 'Testnode'
    assert n1.get_node(register1.uid).name == "Register1"

    assert n2.current_step == 1
    assert round(source2.activation, 2) == 0.7
    assert round(register2.activation, 2) == 0.63
    assert register2.name == "Register2"
    assert source2.name == "Source2"
    assert round(register2.get_slot('gen').get_links()[0].weight, 2) == 0.9
    assert register2.get_slot('gen').get_links()[0].source_node.name == 'Source2'
    assert n2.get_node(register2.uid).name == "Register2"


def test_get_nodespace_changes(fixed_nodenet):
    net = micropsi.nodenets[fixed_nodenet]
    net.step()
    result = micropsi.get_nodespace_changes(fixed_nodenet, [None], 0)
    assert set(result['nodes_dirty'].keys()) == set(net.get_node_uids())
    assert result['nodes_deleted'] == []
    assert result['nodespaces_dirty'] == {}
    assert result['nodespaces_deleted'] == []
    nodes = {}
    for n in net.netapi.get_nodes():
        nodes[n.name] = n
    net.netapi.unlink(nodes['A1'], 'por', nodes['A2'], 'gen')
    net.netapi.delete_node(nodes['B2'])
    newnode = net.netapi.create_node('Pipe', None, "asdf")
    net.netapi.link(newnode, 'gen', nodes['B1'], 'gen')
    newspace = net.netapi.create_nodespace(None, "nodespace")
    net.step()
    test = micropsi.get_nodenet_activation_data(fixed_nodenet, [None], 1)
    assert test['has_changes']
    result = micropsi.get_nodespace_changes(fixed_nodenet, [None], 1)
    assert nodes['B2'].uid in result['nodes_deleted']
    assert nodes['A1'].uid in result['nodes_dirty']
    assert nodes['A2'].uid in result['nodes_dirty']
    assert result['nodes_dirty'][nodes['A1'].uid]['links'] == {}
    assert newnode.uid in result['nodes_dirty']
    assert len(result['nodes_dirty'][newnode.uid]['links']['gen']) == 1
    assert newspace.uid in result['nodespaces_dirty']
    assert len(result['nodes_dirty'].keys()) == 4
    assert len(result['nodespaces_dirty'].keys()) == 1
    net.step()
    test = micropsi.get_nodenet_activation_data(fixed_nodenet, [None], 2)
    assert not test['has_changes']


def test_get_nodespace_changes_cycles(fixed_nodenet):
    net = micropsi.nodenets[fixed_nodenet]
    net.step()
    nodes = {}
    for n in net.netapi.get_nodes():
        nodes[n.name] = n
    net.netapi.delete_node(nodes['B2'])
    net.step()
    result = micropsi.get_nodespace_changes(fixed_nodenet, [None], 1)
    assert nodes['B2'].uid in result['nodes_deleted']
    for i in range(101):
        net.step()
    result = micropsi.get_nodespace_changes(fixed_nodenet, [None], 1)
    assert nodes['B2'].uid not in result['nodes_deleted']


def test_nodespace_properties(test_nodenet):
    data = {'testvalue': 'foobar'}
    rootns = micropsi.get_nodenet(test_nodenet).get_nodespace(None)
    micropsi.set_nodespace_properties(test_nodenet, rootns.uid, data)
    assert micropsi.nodenets[test_nodenet].metadata['nodespace_ui_properties'][rootns.uid] == data
    assert micropsi.get_nodespace_properties(test_nodenet, rootns.uid) == data
    micropsi.save_nodenet(test_nodenet)
    micropsi.revert_nodenet(test_nodenet)
    assert micropsi.get_nodespace_properties(test_nodenet, rootns.uid) == data
    properties = micropsi.get_nodespace_properties(test_nodenet)
    assert properties[rootns.uid] == data
