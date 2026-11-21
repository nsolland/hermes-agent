"""Regression tests for the email adapter's fail-closed TLS boundary.

Extract only the TLS policy function to avoid importing the full gateway or
contacting network services. No actual IMAP/SMTP sockets are opened.
"""
import ast
import logging
import ssl
import unittest
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "plugins/platforms/email/adapter.py"


def load_tls_policy():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    function = next(node for node in tree.body
                    if isinstance(node, ast.FunctionDef)
                    and node.name == "_tls_context")
    module = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
    namespace = {"ssl": ssl, "logger": logging.getLogger(__name__)}
    exec(compile(module, str(SOURCE), "exec"), namespace)
    return namespace["_tls_context"]


class EmailTLSPolicyTests(unittest.TestCase):
    def test_remote_smtp_and_imap_cannot_disable_verification(self):
        policy = load_tls_policy()
        for hostname in ("imap.example.org", "smtp.example.org", "10.0.0.8",
                         "mail.internal", "localhost.evil.test"):
            with self.subTest(hostname=hostname):
                with self.assertRaisesRegex(
                        ValueError, "EMAIL_REMOTE_TLS_VERIFICATION_REQUIRED"):
                    policy(False, hostname)

    def test_verified_remote_connection_uses_verifying_context(self):
        ctx = load_tls_policy()(True, "mail.example.org")
        self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(ctx.check_hostname)

    def test_explicit_local_test_mode_is_loopback_only(self):
        policy = load_tls_policy()
        for host in ("localhost", "127.0.0.1", "::1"):
            with self.subTest(host=host):
                ctx = policy(False, host)
                self.assertEqual(ctx.verify_mode, ssl.CERT_NONE)
                self.assertFalse(ctx.check_hostname)


if __name__ == "__main__":
    unittest.main()
