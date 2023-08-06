
from hamcrest import is_not, contains_string
from prego import TestCase, Task, context, running

from prego.net import localhost, listen_port
from prego.debian import Package, installed


class ContextManagerTests(TestCase):
    def test_simple(self):
        with Task() as task:
            task.command('echo hi')
            task.assert_that(task.lastcmd.stdout.content,
                             contains_string('hi'))

    def test_netcat(self):
        context.port = 2000

        with Task('server', detach=True) as server:
            server.assert_that(Package('nmap'), installed())
            server.assert_that(localhost,
                               is_not(listen_port(context.port)))
            cmd = server.command('ncat -l -p $port')
            server.assert_that(cmd.stdout.content,
                               contains_string('bye'))

        with Task(desc='ncat client') as client:
            client.wait_that(server, running())
            client.wait_that(localhost,
                             listen_port(context.port))
            client.command('ncat -c "echo bye" localhost $port')
