# -*- mode:python; coding:utf-8; tab-width:4 -*-

from prego import TestCase, Task


class pip_tests(TestCase):
    def test_install(self):
        task = Task()
        task.command('python setup.py sdist')
        task.command('virtualenv --clear myenv')
        task.command('. myenv/bin/activate; pip install dist/prego*; echo y | pip uninstall prego; deactivate')
