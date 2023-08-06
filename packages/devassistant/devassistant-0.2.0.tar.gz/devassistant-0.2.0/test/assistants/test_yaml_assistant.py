from flexmock import flexmock
import pytest

from devassistant import exceptions
from devassistant import settings
from devassistant.assistants import yaml_assistant
from devassistant.assistants import snippet
from devassistant.command_helpers import ClHelper, RPMHelper, YUMHelper
from devassistant.yaml_snippet_loader import YamlSnippetLoader

# hook app testing logging
from test.logger import TestLoggingHandler

class TestYamlAssistant(object):
    template_dir = yaml_assistant.YamlAssistant.template_dir

    def setup_method(self, method):
        self.ya = yaml_assistant.YamlAssistant()
        self.ya._files = {'first': {'source': 'f/g'}, 'second': {'source': 's/t'}}
        self.tlh = TestLoggingHandler.create_fresh_handler()

        self.ya2 = yaml_assistant.YamlAssistant()
        self.ya2._files = {}
        self.ya2._run = [{'if $ide':
                            [{'if ls /notachance': [{'log_d': 'ifif'}]},
                             {'else': [{'log_d': 'ifelse'}]}]},
                         {'else': [{'log_d': 'else'}]}]

    # TODO: refactor to also test _dependencies_section alone
    def test_dependencies(self):
        self.ya._dependencies = [{'default': [{'rpm': ['foo', '@bar', 'baz']}]}]
        flexmock(RPMHelper).should_receive('is_rpm_installed').and_return(False, True).one_by_one()
        flexmock(YUMHelper).should_receive('is_group_installed').and_return(False)
        flexmock(YUMHelper).should_receive('install').with_args('foo', '@bar').and_return(True)
        # TODO: rpmhelper is used for checking whether a group was installed - fix
        flexmock(RPMHelper).should_receive('was_rpm_installed').and_return(True, True).one_by_one()
        self.ya.dependencies()

    def test_dependencies_uses_non_default_section_on_param(self):
        self.ya._dependencies = [{'default': [{'rpm': ['foo']}]}, {'_a': [{'rpm': ['bar']}]}]
        flexmock(RPMHelper).should_receive('is_rpm_installed').and_return(False, False).one_by_one()
        flexmock(YUMHelper).should_receive('install').with_args('foo').and_return(True)
        flexmock(YUMHelper).should_receive('install').with_args('bar').and_return(True)
        flexmock(RPMHelper).should_receive('was_rpm_installed').and_return(True)
        self.ya.dependencies(a=True)

    def test_dependencies_does_not_use_non_default_section_when_param_not_present(self):
        self.ya._dependencies = [{'default': [{'rpm': ['foo']}]}, {'_a': [{'rpm': ['bar']}]}]
        flexmock(RPMHelper).should_receive('is_rpm_installed').and_return(False, False).one_by_one()
        flexmock(YUMHelper).should_receive('install').with_args('foo').and_return(True)
        flexmock(RPMHelper).should_receive('was_rpm_installed').and_return(True)
        self.ya.dependencies()

    def test_run_pass(self):
        self.ya._run = [{'cl': 'true'}, {'cl': 'ls'}]
        self.ya.run()

    def test_run_fail(self):
        self.ya._run = [{'cl': 'true'}, {'cl': 'false'}]
        with pytest.raises(exceptions.RunException):
            self.ya.run()

    def test_run_unkown_action(self):
        self.ya._run = [{'foo': 'bar'}]
        self.ya.run()
        assert self.tlh.msgs == [('WARNING', 'Unknown action type foo, skipping.')]

    def test_get_section_to_run_chooses_selected(self):
        self.ya._run = [{'cl': 'ls'}]
        self.ya._run_foo = [{'cl': 'pwd'}]
        section = self.ya._get_section_to_run(section='run', kwargs_override=False, foo=True)
        assert section is self.ya._run

    def test_get_section_to_run_overrides_if_allowed(self):
        self.ya._run = [{'cl': 'ls'}]
        self.ya._run_foo = [{'cl': 'pwd'}]
        section = self.ya._get_section_to_run(section='run', kwargs_override=True, foo=True)
        assert section is self.ya._run_foo

    def test_get_section_to_run_runs_with_None_parameter(self):
        self.ya._run = [{'cl': 'ls'}]
        self.ya._run_foo = [{'cl': 'pwd'}]
        section = self.ya._get_section_to_run(section='run', kwargs_override=True, foo=None)
        assert section is self.ya._run_foo

    def test_run_runs_in_foreground_if_asked(self):
        self.ya._run = [{'cl_f': 'ls'}]
        flexmock(ClHelper).should_receive('run_command').with_args('ls', True, False)
        self.ya.run(foo='bar')

    def test_run_logs_command_at_debug(self):
        # previously, this test used 'ls', but that is in different locations on different
        # distributions (due to Fedora's usrmove), so use something that should be common
        self.ya._run = [{'cl': 'id'}]
        self.ya.run(foo='bar')
        assert self.tlh.msgs == [('DEBUG', settings.COMMAND_LOG_STRING.format(cmd='/usr/bin/id'))]

    def test_run_logs_command_at_info_if_asked(self):
        self.ya._run = [{'cl_i': 'id'}]
        self.ya.run(foo='bar')
        assert self.tlh.msgs == [('INFO', settings.COMMAND_LOG_STRING.format(cmd='/usr/bin/id'))]

    def test_log(self):
        self.ya._run = [{'log_w': 'foo!'}]
        self.ya.run()
        assert self.tlh.msgs == [('WARNING', 'foo!')]

    def test_log_wrong_level(self):
        self.ya._run = [{'log_b': 'bar'}]
        self.ya.run()
        assert self.tlh.msgs == [('WARNING', 'Unknown logging command log_b with message bar')]

    def test_log_formats_message(self):
        self.ya._run = [{'log_i': 'this is $how cool'}]
        self.ya.run(how='very')
        assert self.tlh.msgs == [('INFO', 'this is very cool')]

    def test_run_if_nested_else(self):
        self.ya2.run(ide=True)
        assert ('DEBUG', 'ifelse') in self.tlh.msgs

    def test_run_else(self):
        self.ya2.run()
        assert ('DEBUG', 'else') in self.tlh.msgs

    def test_assign_variable_from_nonexisting_variable(self):
        self.ya._run = [{'$foo': '$bar'}, {'log_i': '$foo'}]
        self.ya.run()
        assert ('INFO', '') in self.tlh.msgs

    def test_assign_variable_from_nonexisting_variable(self):
        self.ya._run = [{'$foo': '$bar'}, {'log_i': '$foo'}]
        bar = 'spam'
        self.ya.run(bar=bar)
        assert ('INFO', 'spam') in self.tlh.msgs

    def test_assign_variable_from_successful_command(self):
        self.ya._run = [{'$foo': 'basename foo/bar'}, {'log_i': '$foo'}]
        self.ya.run()
        assert ('INFO', 'bar') in self.tlh.msgs

    def test_assign_variable_from_unsuccessful_command(self):
        self.ya._run = [{'$foo': 'ls spam/spam/spam'}, {'log_i': '$foo'}]
        self.ya.run()
        assert ('INFO', '') in self.tlh.msgs

    def test_run_snippet(self):
        self.ya._run = [{'snippet': 'mysnippet'}]
        flexmock(YamlSnippetLoader).should_receive('get_snippet_by_name').\
                                    with_args('mysnippet').\
                                    and_return(snippet.Snippet('mysnippet.yaml', {'run': [{'log_i': 'spam'}]}))
        self.ya.run()
        assert ('INFO', 'spam') in self.tlh.msgs
