# Copyright 2018 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock

import zaza.charm_lifecycle.configure as lc_configure
import unit_tests.utils as ut_utils


class TestCharmLifecycleConfigure(ut_utils.BaseTestCase):

    def test_run_configure_list(self):
        self.patch_object(lc_configure.utils, 'get_class')
        self.get_class.side_effect = lambda x: x
        mock1 = mock.MagicMock()
        mock2 = mock.MagicMock()
        lc_configure.run_configure_list([mock1, mock2])
        self.assertTrue(mock1.called)
        self.assertTrue(mock2.called)

    def test_configure(self):
        self.patch_object(lc_configure, 'run_configure_list')
        mock1 = mock.MagicMock()
        mock2 = mock.MagicMock()
        lc_configure.configure('modelname', [mock1, mock2])
        self.run_configure_list.assert_called_once_with([mock1, mock2])

    def test_parser(self):
        args = lc_configure.parse_args(
            ['-m', 'modelname', '-c', 'my.func1', 'my.func2'])
        self.assertEqual(args.configfuncs, ['my.func1', 'my.func2'])
        self.assertEqual(args.model, {'default_alias': 'modelname'})

    def test_parser_logging(self):
        # Using defaults
        args = lc_configure.parse_args(['-m', 'model'])
        self.assertEqual(args.loglevel, 'INFO')
        # Using args
        args = lc_configure.parse_args(['-m', 'model', '--log', 'DEBUG'])
        self.assertEqual(args.loglevel, 'DEBUG')

    def test_main(self):
        self.patch_object(lc_configure.sys, "argv")
        self.patch_object(lc_configure, "cli_utils")
        self.patch_object(lc_configure, "utils")
        mock_args = mock.MagicMock()
        self.patch_object(lc_configure, "parse_args", return_value=mock_args)
        self.patch_object(lc_configure, "configure")
        configfuncs = ["test-config-1", "test-config-2"]

        # no model
        mock_args.model.return_value = {}
        lc_configure.main()
        self.configure.assert_not_called()

        # one model + configuration functions
        mock_args.model = {"test-alias": "test-model"}
        mock_args.configfuncs = configfuncs
        mock_args.test_directory = None

        lc_configure.main()
        self.configure.assert_called_once_with("test-model", configfuncs, None)
        mock_args.reset_mock()
        self.configure.reset_mock()

        # one model + configuration from test.yaml
        mock_args.model = {"test-alias": "test-model"}
        mock_args.configfuncs = None
        mock_args.test_directory = "."
        self.utils.get_config_steps.return_value = {"test-alias": configfuncs}

        lc_configure.main()
        self.utils.set_base_test_dir.assert_called_once_with(test_dir=".")
        self.configure.assert_called_once_with("test-model", configfuncs, ".")
        mock_args.reset_mock()
        self.configure.reset_mock()
