import unittest

class _CommandFaker:

    _orig_COMMANDS = None

    def tearDown(self):
        if self._orig_COMMANDS is not None:
            self._updateCommands(True, **self._orig_COMMANDS)

    def _updateCommands(self, clear=False, **kw):
        from compoze.compozer import _COMMANDS
        orig = _COMMANDS.copy()
        if clear:
            _COMMANDS.clear()
        _COMMANDS.update(kw)
        self._orig_COMMANDS = orig

class Test_get_description(unittest.TestCase, _CommandFaker):

    def _callFUT(self, dotted_or_ep):
        from compoze.compozer import get_description
        return get_description(dotted_or_ep)

    def test_nonesuch(self):
        self.assertRaises(KeyError, self._callFUT, 'nonesuch')

    def test_command_class_wo_docstring(self):
        class Dummy:
            pass
        self._updateCommands(dummy=Dummy)
        self.assertEqual(self._callFUT('dummy'), '')

    def test_command_class_w_docstring(self):
        class Dummy:
            "Dummy Command"
        self._updateCommands(dummy=Dummy)
        self.assertEqual(self._callFUT('dummy'), 'Dummy Command')

class CompozerTests(unittest.TestCase, _CommandFaker):

    _tempdir = None

    def tearDown(self):
        if self._tempdir is not None:
            import shutil
            shutil.rmtree(self._tempdir)

    def _getTargetClass(self):
        from compoze.compozer import Compozer
        return Compozer

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def _makeTempdir(self):
        import tempfile
        self._tempdir = tempfile.mkdtemp()
        return self._tempdir

    def test_ctor_default_options(self):
        compozer = self._makeOne(argv=[])
        self.assertTrue(compozer.options.verbose)
        self.assertEqual(compozer.options.path, '.')
        self.assertEqual(compozer.options.config_files, [])
        self.assertEqual(compozer.options.index_urls,
                         ['http://pypi.python.org/simple'])
        self.assertEqual(compozer.options.find_links, [])
        self.assertFalse(compozer.options.fetch_site_packages)
        self.assertTrue(compozer.options.source_only)
        self.assertFalse(compozer.options.keep_tempdir)
        self.assertEqual(compozer.options.use_versions, False)
        self.assertEqual(compozer.options.versions_section, None)

    def test_ctor_quiet(self):
        compozer = self._makeOne(argv=['--quiet'])
        self.assertFalse(compozer.options.verbose)

    def test_ctor_verbose(self):
        compozer = self._makeOne(argv=['--verbose'])
        self.assertTrue(compozer.options.verbose)

    def test_ctor_one_index_url(self):
        compozer = self._makeOne(
                        argv=['--index-url', 'http://example.com/simple'])
        self.assertEqual(compozer.options.index_urls,
                         ['http://example.com/simple'])

    def test_ctor_multiple_index_urls(self):
        compozer = self._makeOne(
                        argv=['--index-url', 'http://example.com/simple',
                              '--index-url', 'http://example.com/complex',
                             ])
        self.assertEqual(compozer.options.index_urls,
                         ['http://example.com/simple',
                          'http://example.com/complex'])

    def test_ctor_find_links(self):
        compozer = self._makeOne(
                        argv=['--find-links', 'http://example.com/links'])
        self.assertEqual(compozer.options.find_links,
                         ['http://example.com/links'])

    def test_ctor_fetch_site_packages(self):
        compozer = self._makeOne(argv=['--fetch-site-packages'])
        self.assertTrue(compozer.options.fetch_site_packages)

    def test_ctor_use_versions_no_versions_section(self):
        compozer = self._makeOne(argv=['--use-versions'])
        self.assertTrue(compozer.options.use_versions)
        self.assertEqual(compozer.options.versions_section, 'versions')

    def test_ctor_versions_section_no_use_versions(self):
        compozer = self._makeOne(argv=['--versions-section=SECTION'])
        self.assertTrue(compozer.options.use_versions)
        self.assertEqual(compozer.options.versions_section, 'SECTION')

    def test_ctor_source_only(self):
        compozer = self._makeOne(argv=['--include-binary-eggs'])
        self.assertFalse(compozer.options.source_only)

    def test_ctor_keep_tempdir(self):
        compozer = self._makeOne(argv=['--keep-tempdir'])
        self.assertTrue(compozer.options.keep_tempdir)

    def test_ctor_config_file_single(self):
        import os
        dir = self._makeTempdir()
        fn = os.path.join(dir, 'test.cfg')
        f = open(fn, 'w')
        f.writelines(['[global]\n',
                      'path = /tmp/foo\n',
                      'verbose = false\n',
                      'index-url =\n',
                      ' http://example.com/simple\n',
                      ' http://example.com/complex\n',
                      'find-links =\n',
                      ' http://example.com/links\n',
                      'fetch-site-packages = true\n',
                      'include-binary-eggs = false\n',
                      'keep-tempdir = true\n',
                      '\n',
                      '[other]\n',
                      'foo = bar\n',
                      'baz = qux\n'
                     ])
        f.flush()
        f.close()
        compozer = self._makeOne(argv=['--config-file', fn])
        self.assertEqual(compozer.options.config_files, [fn])
        self.assertEqual(compozer.options.config_file_data,
                         {'other': {'foo': 'bar', 'baz': 'qux'}})
        self.assertEqual(compozer.options.path, '/tmp/foo')
        self.assertFalse(compozer.options.verbose)
        self.assertEqual(compozer.options.index_urls,
                         ['http://example.com/simple',
                          'http://example.com/complex'])
        self.assertEqual(compozer.options.find_links,
                         ['http://example.com/links'])
        self.assertTrue(compozer.options.fetch_site_packages)
        self.assertFalse(compozer.options.source_only)
        self.assertTrue(compozer.options.keep_tempdir)

    def test_ctor_config_file_multiple(self):
        import os
        dir = self._makeTempdir()
        fn1 = os.path.join(dir, 'test1.cfg')
        f = open(fn1, 'w')
        f.writelines(['[global]\n',
                      'path = /tmp/foo\n',
                      'verbose = false\n',
                      'index-url =\n',
                      ' http://example.com/simple\n',
                      ' http://example.com/complex\n',
                      'find-links =\n',
                      ' http://example.com/links\n',
                      'fetch-site-packages = true\n',
                      'include-binary-eggs = false\n',
                      'keep-tempdir = true\n',
                      '\n',
                      '[other]\n',
                      'foo = bar\n',
                      'baz = qux\n'
                     ])
        f.flush()
        f.close()
        fn2 = os.path.join(dir, 'test2.cfg')
        f = open(fn2, 'w')
        f.writelines(['[global]\n',
                      'path = /tmp/bar\n',
                      'verbose = true\n',
                      'index-url =\n',
                      ' http://example.com/another\n',
                      'find-links =\n',
                      'fetch-site-packages = false\n',
                      '\n',
                      '[versions]\n',
                      'foo = 1.2.3\n',
                      'baz = < 3.2dev\n'
                     ])
        f.flush()
        f.close()
        compozer = self._makeOne(argv=['--config-file', fn1,
                                       '--config-file', fn2,
                                      ])
        self.assertEqual(compozer.options.config_files, [fn1, fn2])
        self.assertEqual(compozer.options.config_file_data,
                         {'other': {'foo': 'bar', 'baz': 'qux'},
                          'versions': {'foo': '1.2.3', 'baz': '< 3.2dev'}})
        self.assertEqual(compozer.options.path, '/tmp/bar')
        self.assertTrue(compozer.options.verbose)
        self.assertEqual(compozer.options.index_urls,
                         ['http://example.com/another'])
        self.assertEqual(compozer.options.find_links, [])
        self.assertFalse(compozer.options.fetch_site_packages)
        self.assertFalse(compozer.options.source_only)
        self.assertTrue(compozer.options.keep_tempdir)

    def test_ctor_config_file_multiple_merge_versions(self):
        import os
        dir = self._makeTempdir()
        fn1 = os.path.join(dir, 'test1.cfg')
        f = open(fn1, 'w')
        f.writelines(['[versions]\n',
                      'foo = 1.0.1\n',
                      'bar = 0.5\n'
                     ])
        f.flush()
        f.close()
        fn2 = os.path.join(dir, 'test2.cfg')
        f = open(fn2, 'w')
        f.writelines(['[versions]\n',
                      'foo = 1.2.3\n',
                      'baz = < 3.2dev\n'
                     ])
        f.flush()
        f.close()
        compozer = self._makeOne(argv=['--config-file', fn1,
                                       '--config-file', fn2,
                                      ])
        self.assertEqual(compozer.options.config_file_data,
                         {'versions': {'foo': '1.2.3',
                                       'bar': '0.5',
                                       'baz': '< 3.2dev',
                                      }})

    def test_ctor_w_help_commands(self):
        class Dummy:
            """Dummy command"""
        class Other(Dummy):
            """OTher command"""
        self._updateCommands(True, dummy=Dummy, other=Other)
        logged = []
        compozer = self._makeOne(argv=['--help-commands'],
                                 logger=logged.append)
        self.assertEqual(len(logged), 5)
        self.assertEqual(logged[0], 'Valid commands are:')
        self.assertEqual(logged[1], ' dummy')
        self.assertEqual(logged[2], '    ' + Dummy.__doc__)
        self.assertEqual(logged[3], ' other')
        self.assertEqual(logged[4], '    ' + Other.__doc__)

    def test_ctor_w_non_command(self):
        class Dummy:
            """Dummy command"""
        class Other(Dummy):
            """OTher command"""
        self._updateCommands(True, dummy=Dummy, other=Other)
        logged = []
        compozer = self._makeOne(argv=['nonesuch'], logger=logged.append)
        self.assertEqual(len(logged), 5)
        self.assertEqual(logged[0], 'Valid commands are:')
        self.assertEqual(logged[1], ' dummy')
        self.assertEqual(logged[2], '    ' + Dummy.__doc__)
        self.assertEqual(logged[3], ' other')
        self.assertEqual(logged[4], '    ' + Other.__doc__)

    def test_ctor_command_first_no_args(self):
        class Dummy:
            def __init__(self, options, *args):
                self.options = options
                self.args = args
        self._updateCommands(dummy=Dummy)
        compozer = self._makeOne(argv=['dummy'])
        self.assertEqual(len(compozer.commands), 1)
        command = compozer.commands[0]
        self.assertTrue(isinstance(command, Dummy))
        self.assertEqual(command.args, ())

    def test_ctor_command_first_w_args(self):
        class Dummy:
            def __init__(self, options, *args):
                self.options = options
                self.args = args
        self._updateCommands(dummy=Dummy)
        compozer = self._makeOne(argv=['dummy', 'bar', 'baz'])
        self.assertEqual(len(compozer.commands), 1)
        command = compozer.commands[0]
        self.assertEqual(command.args, ('bar', 'baz'))

    def test_ctor_command_multiple_w_args(self):
        class Dummy:
            def __init__(self, options, *args):
                self.options = options
                self.args = args
        class Other(Dummy):
            pass
        self._updateCommands(dummy=Dummy, other=Other)
        compozer = self._makeOne(argv=['dummy', 'bar', 'baz', 'other', 'qux'])
        self.assertEqual(len(compozer.commands), 2)
        command = compozer.commands[0]
        self.assertTrue(isinstance(command, Dummy))
        self.assertEqual(command.args, ('bar', 'baz'))
        command = compozer.commands[1]
        self.assertTrue(isinstance(command, Other))
        self.assertEqual(command.args, ('qux',))

    def test__call___wo_commands(self):
        from compoze.compozer import InvalidCommandLine
        compozer = self._makeOne(argv=[])
        self.assertRaises(InvalidCommandLine, compozer)

    def test___call___w_non_command(self):
        from compoze.compozer import InvalidCommandLine
        logged = []
        compozer = self._makeOne(argv=['nonesuch'], logger=logged.append)
        self.assertRaises(InvalidCommandLine, compozer)

    def test__call___w_commands(self):
        class Dummy:
            called = False
            def __init__(self, options, *args):
                pass
            def __call__(self):
                if self.called:
                    raise ValueError
                self.called = True
        class Other(Dummy):
            pass
        self._updateCommands(dummy=Dummy, other=Other)
        compozer = self._makeOne(argv=['dummy', 'bar', 'baz', 'other', 'qux'])
        compozer()
        self.assertTrue(compozer.commands[0].called)
        self.assertTrue(compozer.commands[1].called)

    def test_error(self):
        class Dummy:
            def __init__(self, options, *args):
                self.options = options
                self.args = args
        self._updateCommands(True, dummy=Dummy)
        logged = []
        compozer = self._makeOne(argv=['dummy'],
                                 logger=logged.append)
        compozer.error('foo')
        self.assertEqual(logged, ['foo'])

    def test_error_not_verbose(self):
        class Dummy:
            def __init__(self, options, *args):
                self.options = options
                self.args = args
        self._updateCommands(True, dummy=Dummy)
        logged = []
        compozer = self._makeOne(argv=['--verbose', 'dummy'],
                                 logger=logged.append)
        compozer.error('foo')
        self.assertEqual(logged, ['foo'])

    def test_error_verbose(self):
        class Dummy:
            def __init__(self, options, *args):
                self.options = options
                self.args = args
        self._updateCommands(True, dummy=Dummy)
        logged = []
        compozer = self._makeOne(argv=['--verbose', 'dummy'],
                                 logger=logged.append)
        compozer.error('foo')
        self.assertEqual(logged, ['foo'])

    def test_blather_not_verbose(self):
        class Dummy:
            def __init__(self, options, *args):
                self.options = options
                self.args = args
        self._updateCommands(True, dummy=Dummy)
        def _dont_go_here(*args):
            assert 0, args
        compozer = self._makeOne(argv=['--quiet', 'dummy'],
                                 logger=_dont_go_here)
        compozer.blather('foo') # doesn't assert

    def test_blather_verbose(self):
        class Dummy:
            def __init__(self, options, *args):
                self.options = options
                self.args = args
        self._updateCommands(True, dummy=Dummy)
        logged = []
        compozer = self._makeOne(argv=['--verbose', 'dummy'],
                                 logger=logged.append)
        compozer.blather('foo')
        self.assertEqual(logged, ['foo'])

class Test_main(unittest.TestCase, _CommandFaker):

    def _callFUT(self, argv):
        from compoze.compozer import main
        return main(argv)

    def test_simple(self):
        called = {}
        class Dummy:
            def __init__(self, options, *args):
                pass
            def __call__(self):
                if self.__class__.__name__ in called:
                    raise ValueError
                called[self.__class__.__name__] = True
        class Other(Dummy):
            pass
        self._updateCommands(dummy=Dummy, other=Other)
        self._callFUT(argv=['dummy', 'bar', 'baz', 'other', 'qux'])
        self.assertTrue('Dummy' in called)
        self.assertTrue('Other' in called)
