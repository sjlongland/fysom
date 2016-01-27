# coding=utf-8
#
# fysom - pYthOn Finite State Machine - this is a port of Jake
#         Gordon's javascript-state-machine to python
#         https://github.com/jakesgordon/javascript-state-machine
#
# Copyright (C) 2011 Mansour Behabadi <mansour@oxplot.com>, Jake Gordon
#                                        and other contributors
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import unittest

from fysom import Fysom, Canceled, HAVE_SIGNALSLOT

@unittest.skipUnless(HAVE_SIGNALSLOT)
class FysomRepeatedBeforeEventSignalTests(unittest.TestCase):

    def setUp(self):
        self.fired = []

        def record_event(event, **kwargs):
            self.fired.append(event.msg)
            return 42

        self.fsm = Fysom({
            'initial': 'notcalled',
            'events': [
                {'name': 'multiple', 'src': 'notcalled', 'dst': 'called'},
                {'name': 'multiple', 'src': 'called', 'dst': 'called'},
            ],
        })
        self.fsm.onbeforemultiple_sig.connect(record_event)

    def test_should_fire_onbefore_event_repeatedly(self):
        self.fsm.multiple(msg="first")
        self.fsm.multiple(msg="second")

        self.assertEqual(self.fired, ["first", "second"])


@unittest.skipUnless(HAVE_SIGNALSLOT)
class FysomRepeatedAfterEventSignalTests(unittest.TestCase):

    def setUp(self):
        self.fired = []

        def record_event(event, **kwargs):
            self.fired.append(event.msg)
            return 42

        self.fsm = Fysom({
            'initial': 'notcalled',
            'events': [
                {'name': 'multiple', 'src': 'notcalled', 'dst': 'called'},
                {'name': 'multiple', 'src': 'called', 'dst': 'called'},
            ],
        })
        self.fsm.onaftermultiple_sig.connect(record_event)

    def test_should_fire_onafter_event_repeatedly(self):
        self.fsm.multiple(msg="first")
        self.fsm.multiple(msg="second")

        self.assertEqual(self.fired, ["first", "second"])


@unittest.skipUnless(HAVE_SIGNALSLOT)
class FysomSignalTests(unittest.TestCase):

    def before_foo(self, event, **kwargs):
        self.before_foo_event = event
        self.fired_signals.append('before_foo')

    def before_bar(self, event, **kwargs):
        self.before_bar_event = event
        self.fired_signals.append('before_bar')

    def before_wait(self, event, **kwargs):
        self.before_wait_event = event
        self.fired_signals.append('before_wait')
        return False

    def on_foo(self, event, **kwargs):
        self.foo_event = event
        self.fired_signals.append('after_foo')

    def on_bar(self, event, **kwargs):
        self.bar_event = event
        self.fired_signals.append('after_bar')

    def on_baz(self, event, **kwargs):
        raise ValueError('Baz-inga!')

    def on_enter_fooed(self, event, **kwargs):
        self.enter_fooed_event = event

    def on_enter_bared(self, event, **kwargs):
        self.enter_bared_event = event

    def on_reenter_fooed(self, event, **kwargs):
        self.reenter_fooed_event = event

    def on_reenter_bared(self, event, **kwargs):
        self.reenter_bared_event = event

    def on_leave_sleeping(self, event, **kwargs):
        self.leave_sleeping_event = event

    def on_leave_fooed(self, event, **kwargs):
        self.leave_fooed_event = event

    def setUp(self):
        self.fired_signals = []

        self.fsm = Fysom({
            'initial': 'sleeping',
            'events': [
                {'name': 'foo', 'src': 'sleeping', 'dst': 'fooed'},
                {'name': 'foo', 'src': 'fooed', 'dst': 'fooed'},
                {'name': 'bar', 'src': 'fooed', 'dst': 'bared'},
                {'name': 'bar', 'src': 'bared', 'dst': 'bared'},
                {'name': 'baz', 'src': 'bared', 'dst': 'bazed'},
                {'name': 'wait', 'src': 'sleeping', 'dst': 'waiting'}
            ],
        })
        self.fsm.onfoo_sig.connect(self.on_foo)
        self.fsm.onbar_sig.connect(self.on_bar)
        self.fsm.onbaz_sig.connect(self.on_baz)
        self.fsm.onbeforefoo_sig.connect(self.before_foo)
        self.fsm.onbeforebar_sig.connect(self.before_bar)
        self.fsm.onbeforewait_sig.connect(self.before_wait)
        self.fsm.onenterfooed_sig.connect(self.on_enter_fooed)
        self.fsm.onenterbared_sig.connect(self.on_enter_bared)
        self.fsm.onreenterfooed_sig.connect(self.on_reenter_fooed)
        self.fsm.onreenterbared_sig.connect(self.on_reenter_bared)
        self.fsm.onleavesleeping_sig.connect(self.on_leave_sleeping)
        self.fsm.onleavefooed_sig.connect(self.on_leave_fooed)

    def test_onafter_event_signals_should_fire_with_keyword_arguments_when_events_occur(self):
        self.fsm.foo(attribute='test')
        self.assertTrue(
            hasattr(self, 'foo_event'), 'Callback on_foo did not fire.')
        self.assertTrue(self.foo_event is not None)
        self.assertEqual(self.foo_event.attribute, 'test')

        self.fsm.bar(id=123)
        self.assertTrue(
            hasattr(self, 'bar_event'), 'Callback on_bar did not fire.')
        self.assertTrue(self.bar_event is not None)
        self.assertEqual(self.bar_event.id, 123)

    def test_onafter_event_signals_raising_exceptions_should_not_be_eaten(self):
        self.fsm.foo()
        self.fsm.bar()
        self.assertRaises(ValueError, self.fsm.baz)

    def test_onbefore_event_signals_should_fire_before_onafter_signals_with_keyword_arguments_when_events_occur(
            self):
        self.fsm.foo(attribute='test')
        self.assertTrue(
            hasattr(self, 'before_foo_event'), 'Callback onbeforefoo did not fire.')
        self.assertTrue(self.before_foo_event is not None)
        self.assertEqual(self.before_foo_event.attribute, 'test')
        self.fsm.bar(id=123)
        self.assertTrue(
            hasattr(self, 'before_bar_event'), 'Callback onbeforebar did not fire.')
        self.assertTrue(self.before_bar_event is not None)
        self.assertEqual(self.before_bar_event.id, 123)
        self.assertEqual(
            ['before_foo', 'after_foo', 'before_bar', 'after_bar'], self.fired_signals)

    def test_fsm_cancel_transition_when_onbefore_event_signals_return_false(self):
        self.assertRaises(Canceled, self.fsm.wait)
        self.assertEqual(self.fsm.current, 'sleeping')

    def test_onenter_state_signals_should_fire_with_keyword_arguments_when_state_transitions_occur(self):
        self.fsm.foo(attribute='test')
        self.assertTrue(
            hasattr(self, 'enter_fooed_event'), 'Callback onenterfooed did not fire.')
        self.assertTrue(self.enter_fooed_event is not None)
        self.assertEqual(self.enter_fooed_event.attribute, 'test')

        self.fsm.bar(id=123)
        self.assertTrue(
            hasattr(self, 'enter_bared_event'), 'Callback onenterbared did not fire.')
        self.assertTrue(self.enter_bared_event is not None)
        self.assertEqual(self.enter_bared_event.id, 123)

    def test_onreenter_state_signals_should_fire_with_keyword_arguments_when_state_transitions_occur(self):
        self.fsm.foo(attribute='testfail')
        self.fsm.foo(attribute='testpass')
        self.assertTrue(
            hasattr(self, 'reenter_fooed_event'), 'Callback onreenterfooed did not fire.')
        self.assertTrue(self.reenter_fooed_event is not None)
        self.assertEqual(self.reenter_fooed_event.attribute, 'testpass')

        self.fsm.bar(id=1234)
        self.fsm.bar(id=4321)
        self.assertTrue(
            hasattr(self, 'reenter_bared_event'), 'Callback onreenterbared did not fire.')
        self.assertTrue(self.reenter_bared_event is not None)
        self.assertEqual(self.reenter_bared_event.id, 4321)

    def test_onleave_state_signals_should_fire_with_keyword_arguments_when_state_transitions_occur(self):
        self.fsm.foo(attribute='test')
        self.assertTrue(hasattr(self, 'leave_sleeping_event'),
                        'Callback onleavesleeping did not fire.')
        self.assertTrue(self.leave_sleeping_event is not None)
        self.assertEqual(self.leave_sleeping_event.attribute, 'test')

        self.fsm.bar(id=123)
        self.assertTrue(
            hasattr(self, 'leave_fooed_event'), 'Callback onleavefooed did not fire.')
        self.assertTrue(self.leave_fooed_event is not None)
        self.assertEqual(self.leave_fooed_event.id, 123)

    def test_onchangestate_should_fire_for_all_state_changes(self):
        def on_change_state(event, **kwargs):
            self.current_event = event
        fsm = Fysom({
            'initial': 'foo',
            'events': [
                {'name': 'footobar', 'src': 'foo', 'dst': 'bar'},
                {'name': 'bartobaz', 'src': 'bar', 'dst': 'baz'},
            ],
        })
        fsm.onchangestate_sig.connect(on_change_state)

        fsm.footobar(id=123)
        self.assertEqual(self.current_event.event, 'footobar')
        self.assertEqual(self.current_event.src, 'foo')
        self.assertEqual(self.current_event.dst, 'bar')
        self.assertEqual(self.current_event.id, 123)
        self.assertTrue(self.current_event.fsm is fsm)

        fsm.bartobaz('positional', named_attribute='test')
        self.assertEqual(self.current_event.event, 'bartobaz')
        self.assertEqual(self.current_event.src, 'bar')
        self.assertEqual(self.current_event.dst, 'baz')
        self.assertEqual(self.current_event.named_attribute, 'test')
        self.assertEqual(self.current_event.args[0], 'positional')
        self.assertTrue(self.current_event.fsm is fsm)

    def test_before_event_can_cancel(self):
        def on_before(event, **kwargs):
            self.current_event = event
            return False
        fsm = Fysom({
            'initial': 'foo',
            'events': [
                {'name': 'footobar', 'src': 'foo', 'dst': 'bar'},
                {'name': 'bartobaz', 'src': 'bar', 'dst': 'baz'},
            ],
        })
        fsm.onbeforefootobar_sig.connect(on_before)

        self.assertRaises(Canceled, fsm.footobar, id=42)
        self.assertEqual(self.current_event.event, 'footobar')
        self.assertEqual(self.current_event.src, 'foo')
        self.assertEqual(self.current_event.dst, 'bar')
        self.assertEqual(self.current_event.id, 42)
        self.assertTrue(self.current_event.fsm is fsm)

    def test_leave_state_can_abort(self):
        def on_leave(event, **kwargs):
            self.current_event = event
            return False
        fsm = Fysom({
            'initial': 'foo',
            'events': [
                {'name': 'footobar', 'src': 'foo', 'dst': 'bar'},
                {'name': 'bartobaz', 'src': 'bar', 'dst': 'baz'},
            ],
        })
        fsm.onleavefoo_sig.connect(on_leave)

        fsm.footobar(id=42)
        self.assertEqual(self.current_event.event, 'footobar')
        self.assertEqual(self.current_event.src, 'foo')
        self.assertEqual(self.current_event.dst, 'bar')
        self.assertEqual(self.current_event.id, 42)
        self.assertTrue(self.current_event.fsm is fsm)
        self.assertEqual(fsm.current, 'foo')
