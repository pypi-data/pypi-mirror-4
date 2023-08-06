# -*- mode:python; coding:utf-8; tab-width:4 -*-

from prego import TestCase, Task


class pip_tests(TestCase):
    def test_install(self):
        task = Task()
        task.command('rm dist/*')
        task.command('python setup.py sdist')
        task.command('virtualenv --clear --no-site-packages venv')
        task.command('. venv/bin/activate; pip install prego; echo y | pip uninstall prego; deactivate', timeout=20)
