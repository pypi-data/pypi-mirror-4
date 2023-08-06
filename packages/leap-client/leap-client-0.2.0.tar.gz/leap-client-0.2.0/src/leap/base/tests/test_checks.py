try:
    import unittest2 as unittest
except ImportError:
    import unittest
import os
import sh

from mock import (patch, Mock)
from StringIO import StringIO

from leap.base import checks
from leap.base import exceptions
from leap.testing.basetest import BaseLeapTest

_uid = os.getuid()


class LeapNetworkCheckTest(BaseLeapTest):
    __name__ = "leap_network_check_tests"

    def setUp(self):
        os.environ['PATH'] += ':/bin'
        pass

    def tearDown(self):
        pass

    def test_checker_should_implement_check_methods(self):
        checker = checks.LeapNetworkChecker()

        self.assertTrue(hasattr(checker, "check_internet_connection"),
                        "missing meth")
        self.assertTrue(hasattr(checker, "check_tunnel_default_interface"),
                        "missing meth")
        self.assertTrue(hasattr(checker, "is_internet_up"),
                        "missing meth")
        self.assertTrue(hasattr(checker, "ping_gateway"),
                        "missing meth")
        self.assertTrue(hasattr(checker, "parse_log_and_react"),
                        "missing meth")

    def test_checker_should_actually_call_all_tests(self):
        checker = checks.LeapNetworkChecker()
        mc = Mock()
        checker.run_all(checker=mc)
        self.assertTrue(mc.check_internet_connection.called, "not called")
        self.assertTrue(mc.check_tunnel_default_interface.called, "not called")
        self.assertTrue(mc.is_internet_up.called, "not called")
        self.assertTrue(mc.parse_log_and_react.called, "not called")

        # ping gateway only called if we pass provider_gw
        checker = checks.LeapNetworkChecker(provider_gw="0.0.0.0")
        mc = Mock()
        checker.run_all(checker=mc)
        self.assertTrue(mc.check_internet_connection.called, "not called")
        self.assertTrue(mc.check_tunnel_default_interface.called, "not called")
        self.assertTrue(mc.ping_gateway.called, "not called")
        self.assertTrue(mc.is_internet_up.called, "not called")
        self.assertTrue(mc.parse_log_and_react.called, "not called")

    def test_get_default_interface_no_interface(self):
        checker = checks.LeapNetworkChecker()
        with patch('leap.base.checks.open', create=True) as mock_open:
            with self.assertRaises(exceptions.NoDefaultInterfaceFoundError):
                mock_open.return_value = StringIO(
                    "Iface\tDestination Gateway\t"
                    "Flags\tRefCntd\tUse\tMetric\t"
                    "Mask\tMTU\tWindow\tIRTT")
                checker.get_default_interface_gateway()

    def test_check_tunnel_default_interface(self):
        checker = checks.LeapNetworkChecker()
        with patch('leap.base.checks.open', create=True) as mock_open:
            with self.assertRaises(exceptions.TunnelNotDefaultRouteError):
                mock_open.return_value = StringIO(
                    "Iface\tDestination Gateway\t"
                    "Flags\tRefCntd\tUse\tMetric\t"
                    "Mask\tMTU\tWindow\tIRTT\n"
                    "wlan0\t00000000\t0102A8C0\t"
                    "0003\t0\t0\t0\t00000000\t0\t0\t0")
                checker.check_tunnel_default_interface()

        with patch('leap.base.checks.open', create=True) as mock_open:
            mock_open.return_value = StringIO(
                "Iface\tDestination Gateway\t"
                "Flags\tRefCntd\tUse\tMetric\t"
                "Mask\tMTU\tWindow\tIRTT\n"
                "tun0\t00000000\t01002A0A\t0003\t0\t0\t0\t00000080\t0\t0\t0")
            checker.check_tunnel_default_interface()

    def test_ping_gateway_fail(self):
        checker = checks.LeapNetworkChecker()
        with patch.object(sh, "ping") as mocked_ping:
            with self.assertRaises(exceptions.NoConnectionToGateway):
                mocked_ping.return_value = Mock
                mocked_ping.return_value.stdout = "11% packet loss"
                checker.ping_gateway("4.2.2.2")

    def test_ping_gateway(self):
        checker = checks.LeapNetworkChecker()
        with patch.object(sh, "ping") as mocked_ping:
            mocked_ping.return_value = Mock
            mocked_ping.return_value.stdout = """
PING 4.2.2.2 (4.2.2.2) 56(84) bytes of data.
64 bytes from 4.2.2.2: icmp_req=1 ttl=54 time=33.8 ms
64 bytes from 4.2.2.2: icmp_req=2 ttl=54 time=30.6 ms
64 bytes from 4.2.2.2: icmp_req=3 ttl=54 time=31.4 ms
64 bytes from 4.2.2.2: icmp_req=4 ttl=54 time=36.1 ms
64 bytes from 4.2.2.2: icmp_req=5 ttl=54 time=30.8 ms
64 bytes from 4.2.2.2: icmp_req=6 ttl=54 time=30.4 ms
64 bytes from 4.2.2.2: icmp_req=7 ttl=54 time=30.7 ms
64 bytes from 4.2.2.2: icmp_req=8 ttl=54 time=32.7 ms
64 bytes from 4.2.2.2: icmp_req=9 ttl=54 time=31.4 ms
64 bytes from 4.2.2.2: icmp_req=10 ttl=54 time=33.3 ms

--- 4.2.2.2 ping statistics ---
10 packets transmitted, 10 received, 0% packet loss, time 9016ms
rtt min/avg/max/mdev = 30.497/32.172/36.161/1.755 ms"""
        checker.ping_gateway("4.2.2.2")

    def test_check_internet_connection_failures(self):
        checker = checks.LeapNetworkChecker()
        TimeoutError = get_ping_timeout_error()
        with patch.object(sh, "ping") as mocked_ping:
            mocked_ping.side_effect = TimeoutError
            with self.assertRaises(exceptions.NoInternetConnection):
                with patch.object(checker, "ping_gateway") as mock_gateway:
                    mock_gateway.side_effect = exceptions.NoConnectionToGateway
                    checker.check_internet_connection()

        with patch.object(sh, "ping") as mocked_ping:
            mocked_ping.side_effect = TimeoutError
            with self.assertRaises(exceptions.NoInternetConnection):
                with patch.object(checker, "ping_gateway") as mock_gateway:
                    mock_gateway.return_value = True
                    checker.check_internet_connection()

    def test_parse_log_and_react(self):
        checker = checks.LeapNetworkChecker()
        to_call = Mock()
        log = [("leap.openvpn - INFO - Mon Nov 19 13:36:24 2012 "
                "read UDPv4 [ECONNREFUSED]: Connection refused (code=111)")]
        err_matrix = [(checks.EVENT_CONNECT_REFUSED, (to_call, ))]
        checker.parse_log_and_react(log, err_matrix)
        self.assertTrue(to_call.called)

        log = [("2012-11-19 13:36:26,177 - leap.openvpn - INFO - "
                "Mon Nov 19 13:36:24 2012 ERROR: Linux route delete command "
                "failed: external program exited"),
               ("2012-11-19 13:36:26,178 - leap.openvpn - INFO - "
                "Mon Nov 19 13:36:24 2012 ERROR: Linux route delete command "
                "failed: external program exited"),
               ("2012-11-19 13:36:26,180 - leap.openvpn - INFO - "
                "Mon Nov 19 13:36:24 2012 ERROR: Linux route delete command "
                "failed: external program exited"),
               ("2012-11-19 13:36:26,181 - leap.openvpn - INFO - "
                "Mon Nov 19 13:36:24 2012 /sbin/ifconfig tun0 0.0.0.0"),
               ("2012-11-19 13:36:26,182 - leap.openvpn - INFO - "
                "Mon Nov 19 13:36:24 2012 Linux ip addr del failed: external "
                "program exited with error stat"),
               ("2012-11-19 13:36:26,183 - leap.openvpn - INFO - "
                "Mon Nov 19 13:36:26 2012 SIGTERM[hard,] received, process"
                "exiting"), ]
        to_call.reset_mock()
        checker.parse_log_and_react(log, err_matrix)
        self.assertFalse(to_call.called)

        to_call.reset_mock()
        checker.parse_log_and_react([], err_matrix)
        self.assertFalse(to_call.called)


def get_ping_timeout_error():
    try:
        sh.ping("-c", "1", "-w", "1", "8.8.7.7")
    except Exception as e:
        return e
