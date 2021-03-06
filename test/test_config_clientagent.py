#!/usr/bin/env python2
import unittest
import subprocess
import threading
import tempfile
import os

from testdc import *

DAEMON_PATH = './astrond'
TERMINATED = -15
EXITED = 1

class ConfigTest(object):
    def __init__(self, config):
        self.config = config
        self.process = None

    def run(self, timeout):
        def target():
            self.process = subprocess.Popen([DAEMON_PATH, self.config])
            self.process.communicate()

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()
            return TERMINATED
        return EXITED

class TestConfigClientAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cfg, cls.config_file = tempfile.mkstemp()
        os.close(cfg)

        cls.test_command = ConfigTest(cls.config_file)

    @classmethod
    def tearDownClass(cls):
        if cls.config_file is not None:
            os.remove(cls.config_file)

    @classmethod
    def write_config(cls, config):
        f = open(cls.config_file, "w")
        f.write(config)
        f.close()

    @classmethod
    def run_test(cls, config, timeout = 2):
        cls.write_config(config)
        return cls.test_command.run(timeout)

    def test_clientagent_good(self):
        config = """\
            messagedirector:
                bind: 127.0.0.1:57123

            general:
                dc_files:
                    - %r

            uberdogs:
                - id: 1234
                  class: UberDog1
                  anonymous: true

                - id: 1235
                  class: UberDog2
                  anonymous: false

            roles:
                - type: clientagent
                  bind: 127.0.0.1:57128
                  version: "Sword Art Online v5.1"
                  channels:
                      min: 3100
                      max: 3999
                  client:
                      relocate: true
                      add_interest: enabled

                - type: clientagent
                  bind: 127.0.0.1:57135
                  version: "Sword Art Online v5.1"
                  client:
                      type: libastron
                      add_interest: disabled
                  channels:
                      min: 110600
                      max: 110699

                - type: clientagent
                  bind: 127.0.0.1:57144
                  version: "Sword Art Online v5.1"
                  client:
                      type: libastron
                      add_interest: visible
                  channels:
                      min: 220600
                      max: 220699
            """ % test_dc
        self.assertEquals(self.run_test(config), TERMINATED)

    def test_ca_invalid_attr(self):
        config = """\
            messagedirector:
                bind: 127.0.0.1:57123

            roles:
                - type: clientagent
                  bind: 127.0.0.1:57128
                  version: "Sword Art Online v5.1"
                  channels:
                      min: 3100
                      max: 3999
                  weeuuweeeuu: sirens!
            """
        self.assertEquals(self.run_test(config), EXITED)

    def test_ca_invalid_channels(self):
        config = """\
            messagedirector:
                bind: 127.0.0.1:57123

            roles:
                - type: clientagent
                  bind: 127.0.0.1:57128
                  version: "Sword Art Online v5.1"
                  channels:
                      min: 0
                      max: 3999
            """
        self.assertEquals(self.run_test(config), EXITED)

        config = """\
            messagedirector:
                bind: 127.0.0.1:57123

            roles:
                - type: clientagent
                  bind: 127.0.0.1:57128
                  version: "Sword Art Online v5.1"
                  channels:
                      min: 3100
                      max: 0
            """
        self.assertEquals(self.run_test(config), EXITED)

    def test_ca_reserved_channels(self):
        config = """\
            messagedirector:
                bind: 127.0.0.1:57123

            roles:
                - type: clientagent
                  bind: 127.0.0.1:57128
                  version: "Sword Art Online v5.1"
                  channels:
                      min: 100
                      max: 3999
            """
        self.assertEquals(self.run_test(config), EXITED)

        config = """\
            messagedirector:
                bind: 127.0.0.1:57123

            roles:
                - type: clientagent
                  bind: 127.0.0.1:57128
                  version: "Sword Art Online v5.1"
                  channels:
                      min: 3100
                      max: 999
            """
        self.assertEquals(self.run_test(config), EXITED)

    def test_ca_client_type_typo(self):
        config = """\
            messagedirector:
                bind: 127.0.0.1:57123

            roles:
                - type: clientagent
                  bind: 127.0.0.1:57128
                  version: "Sword Art Online v5.1"
                  client:
                      type: astron
                  channels:
                      min: 3100
                      max: 3999
            """
        self.assertEquals(self.run_test(config), EXITED)

    def test_ca_bind_address(self):
        config = """\
            messagedirector:
                bind: 127.0.0.1:57123

            roles:
                - type: clientagent
                  bind: pizza:2314
                  version: "Sword Art Online v5.1"
                  channels:
                      min: 3100
                      max: 3999
            """
        self.assertEquals(self.run_test(config), EXITED)

        # ipv6 test disabled because client agent can't accept them yet, and causes a crash
        config = """\
            messagedirector:
                bind: 127.0.0.1:57123

            roles:
                - type: clientagent
                  bind: ::1:2314
                  version: "Sword Art Online v5.1"
                  channels:
                      min: 3100
                      max: 3999
            """
        #self.assertEquals(self.run_test(config), TERMINATED)

if __name__ == '__main__':
    unittest.main()
