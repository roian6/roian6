import base64
import contextlib
import hashlib
import io
import json
import os
import socket
import ssl
import unittest
import urllib.error
from unittest.mock import patch

import update_tokscale_card as card


VALID = b'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" data-template="graph" width="680"
 height="240" aria-label="Tokscale contribution graph for @roian6">
 <defs><style>text{font-variant-numeric:tabular-nums}</style></defs>
 <text>@roian6</text><text>Tokscale</text><text>Tokens</text><text>Cost</text>
 <g data-contribution-panel="true"><text>Contribution activity</text>
 <rect width="10" height="10" fill="#388bfd"><title>2026-10-19 - level 1</title></rect>
 </g></svg>'''
TOKEN = "test-credential-never-public"
API = "https://api.github.com/repos/roian6/roian6/contents/tokscale.svg"
READ = API + "?ref=profile-assets"
SOURCE = "https://tokscale.ai/api/embed/roian6/svg?template=graph&color=blue&theme=dark&sort=cost&rank=plain&tokens=compact&cost=compact"


def asset(body=VALID, **overrides):
    value = {
        "type": "file", "name": "tokscale.svg", "path": "tokscale.svg",
        "encoding": "base64", "content": base64.encodebytes(body).decode(),
        "sha": hashlib.sha1(b"blob " + str(len(body)).encode() + b"\0" + body).hexdigest(),
        "size": len(body),
    }
    value.update(overrides)
    return json.dumps(value).encode()


def http_error(status):
    return urllib.error.HTTPError(SOURCE, status, TOKEN, {}, io.BytesIO(TOKEN.encode()))


class Response(io.BytesIO):
    status = 200


class Transport:
    def __init__(self, outcomes):
        self.outcomes = iter(outcomes)
        self.requests = []
        self.limits = []

    def open(self, request, timeout):
        self.requests.append(request)
        if timeout != 45:
            raise AssertionError("Socket timeout must be 45 seconds")
        outcome = next(self.outcomes)
        if isinstance(outcome, urllib.error.HTTPError):
            raise http_error(outcome.code)
        if isinstance(outcome, Exception):
            raise outcome
        response = Response(outcome)
        original_read = response.read

        def bounded_read(limit=-1):
            self.limits.append(limit)
            if limit <= 0:
                raise AssertionError("Unbounded read")
            return original_read(limit)

        response.read = bounded_read
        return response


class IOTests(unittest.TestCase):
    def run_card(self, outcomes, environment=None):
        transport = Transport(outcomes)
        stderr, stdout = io.StringIO(), io.StringIO()
        environment = environment if environment is not None else {
            "GITHUB_TOKEN": TOKEN, "GITHUB_REPOSITORY": "roian6/roian6",
        }
        with (
            patch.dict(os.environ, environment, clear=True),
            patch.object(card.urllib.request, "build_opener", return_value=transport),
            patch.object(card.time, "sleep") as sleep,
            contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(stdout),
        ):
            result = card.main()
        return result, transport, stderr.getvalue() + stdout.getvalue(), sleep.call_args_list

    def test_unchanged_asset_has_no_commit(self):
        result, transport, output, sleeps = self.run_card([VALID, asset()])
        self.assertEqual(result, 0, output)
        self.assertEqual([(r.method, r.full_url) for r in transport.requests],
                         [("GET", SOURCE), ("GET", READ)])
        self.assertEqual(sleeps, [])
        self.assertLessEqual(transport.limits[0], 256 * 1024 + 1)

    def test_changed_asset_has_one_cas_update_and_readback(self):
        old = VALID.replace(b"level 1", b"level 0")
        result, transport, output, _ = self.run_card([VALID, asset(old), b"{}", asset()])
        self.assertEqual(result, 0, output)
        self.assertEqual([(r.method, r.full_url) for r in transport.requests],
                         [("GET", SOURCE), ("GET", READ), ("PUT", API), ("GET", READ)])
        payload = json.loads(transport.requests[2].data)
        bot = {"name": "github-actions[bot]", "email": "41898282+github-actions[bot]@users.noreply.github.com"}
        self.assertEqual(payload, {
            "message": "Update Tokscale card", "branch": "profile-assets",
            "sha": json.loads(asset(old))["sha"], "content": base64.b64encode(VALID).decode(),
            "author": bot, "committer": bot,
        })

    def test_credentials_are_only_sent_to_fixed_github_target(self):
        _, transport, output, _ = self.run_card([VALID, asset(b"old"), b"{}", asset()])
        source, *github = transport.requests
        self.assertNotIn("Authorization", dict(source.header_items()))
        self.assertNotIn(TOKEN, repr(source.header_items()) + source.full_url + output)
        for request in github:
            self.assertEqual(request.get_header("Authorization"), "Bearer " + TOKEN)
            self.assertIn(request.full_url, (API, READ))

    def test_invalid_sources_never_access_hosted_asset(self):
        for body in (b"<svg", b"<html>Error</html>", VALID.replace(b"Tokens", b"Error")):
            with self.subTest(body=body):
                result, transport, output, _ = self.run_card([body] * 3)
                self.assertEqual(result, 1)
                self.assertTrue(all(r.full_url == SOURCE for r in transport.requests))
                self.assertNotIn(TOKEN, output)

    def test_previous_success_survives_a_later_source_failure(self):
        result, _, output, _ = self.run_card([VALID, asset(b"old"), b"{}", asset()])
        self.assertEqual(result, 0, output)
        result, transport, _, _ = self.run_card([b"<svg"] * 3)
        self.assertEqual(result, 1)
        self.assertEqual([r.full_url for r in transport.requests], [SOURCE] * 3)

    def test_read_failure_does_not_trigger_a_second_write(self):
        result, transport, output, _ = self.run_card([VALID, asset(b"old"), b"{}", http_error(401)])
        self.assertEqual(result, 1)
        self.assertEqual([r.method for r in transport.requests], ["GET", "GET", "PUT", "GET"])
        self.assertIn("uncertain", output.lower())

    def test_temporary_error_card_can_recover(self):
        error_card = b'<svg xmlns="http://www.w3.org/2000/svg"><text>Service unavailable</text></svg>'
        result, transport, output, _ = self.run_card([error_card, VALID, asset()])
        self.assertEqual(result, 0, output)
        self.assertEqual([r.full_url for r in transport.requests], [SOURCE, SOURCE, READ])

    def test_transient_source_failures_retry_at_most_three_times(self):
        for failure in (http_error(429), http_error(503), TimeoutError(TOKEN),
                        urllib.error.URLError(socket.gaierror(socket.EAI_AGAIN, TOKEN)), b"<svg"):
            with self.subTest(failure=type(failure).__name__):
                result, transport, _, sleeps = self.run_card([failure] * 3)
                self.assertEqual(result, 1)
                self.assertEqual(len(transport.requests), 3)
                self.assertEqual([c.args[0] for c in sleeps], [1, 2])

    def test_transient_source_recovers_before_github_read(self):
        result, transport, output, _ = self.run_card([http_error(502), b"<svg", VALID, asset()])
        self.assertEqual(result, 0, output)
        self.assertEqual([r.full_url for r in transport.requests], [SOURCE] * 3 + [READ])

    def test_permanent_source_failures_are_visible_without_retry(self):
        failures = [http_error(c) for c in (301, 400, 401, 403, 404)] + [
            urllib.error.URLError(ssl.SSLCertVerificationError(TOKEN)),
            urllib.error.URLError(socket.gaierror(socket.EAI_NONAME, TOKEN)),
            VALID.replace(b"@roian6", b"@other"), b"x" * (256 * 1024 + 1),
        ]
        for failure in failures:
            with self.subTest(failure=type(failure).__name__):
                result, transport, output, sleeps = self.run_card([failure])
                self.assertEqual(result, 1)
                self.assertEqual(len(transport.requests), 1)
                self.assertEqual(sleeps, [])
                self.assertNotIn(TOKEN, output)

    def test_missing_token_or_wrong_repository_performs_no_io(self):
        for environment in ({}, {"GITHUB_TOKEN": ""},
                            {"GITHUB_TOKEN": TOKEN, "GITHUB_REPOSITORY": "other/repo"},
                            {"GITHUB_TOKEN": TOKEN, "GITHUB_REPOSITORY": ""}):
            with self.subTest(keys=list(environment)):
                result, transport, output, _ = self.run_card([], environment)
                self.assertEqual(result, 1)
                self.assertEqual(transport.requests, [])
                self.assertNotIn(TOKEN, output)

    def test_repository_variable_can_be_absent(self):
        result, _, output, _ = self.run_card([VALID, asset()], {"GITHUB_TOKEN": TOKEN})
        self.assertEqual(result, 0, output)

    def test_bad_current_asset_never_causes_put(self):
        malformed = [b"null", b"[]", b"{", asset(type="symlink"), asset(encoding="none"),
                     asset(content="!"), asset(content=3), asset(sha=""), asset(size=1),
                     asset(path="other.svg"), asset(name="other.svg"), asset(sha=42),
                     asset(submodule_git_url="https://example.com"),
                     b"x" * (512 * 1024 + 1), http_error(404), http_error(401)]
        for body in malformed:
            with self.subTest(body=type(body).__name__):
                result, transport, output, _ = self.run_card([VALID, body])
                self.assertEqual(result, 1)
                self.assertEqual([r.method for r in transport.requests], ["GET", "GET"])
                self.assertNotIn(TOKEN, output)

    def test_ambiguous_write_is_read_back_once_without_retry(self):
        for failure in (TimeoutError(TOKEN), http_error(500), http_error(429)):
            with self.subTest(failure=type(failure).__name__):
                result, transport, output, sleeps = self.run_card([VALID, asset(b"old"), failure, asset()])
                self.assertEqual(result, 0, output)
                self.assertEqual([r.method for r in transport.requests], ["GET", "GET", "PUT", "GET"])
                self.assertEqual(sleeps, [])
                self.assertNotIn(TOKEN, output)

    def test_uncertain_write_fails_and_never_loops(self):
        for readback in (asset(b"old"), asset(b"concurrent"), http_error(503), b"null"):
            with self.subTest(readback=type(readback).__name__):
                result, transport, output, sleeps = self.run_card([
                    VALID, asset(b"old"), TimeoutError(TOKEN), readback,
                ])
                self.assertEqual(result, 1)
                self.assertEqual([r.method for r in transport.requests], ["GET", "GET", "PUT", "GET"])
                self.assertIn("uncertain", output.lower())
                self.assertEqual(sleeps, [])

    def test_rejected_write_is_visible_without_retry(self):
        for status in (401, 403, 404, 409, 422):
            with self.subTest(status=status):
                result, transport, output, sleeps = self.run_card([VALID, asset(b"old"), http_error(status)])
                self.assertEqual(result, 1)
                self.assertEqual([r.method for r in transport.requests], ["GET", "GET", "PUT"])
                self.assertIn(str(status), output)
                self.assertNotIn(TOKEN, output)
                self.assertEqual(sleeps, [])

    def test_successful_write_requires_matching_readback(self):
        result, transport, output, _ = self.run_card([VALID, asset(b"old"), b"{}", asset(b"old")])
        self.assertEqual(result, 1)
        self.assertEqual(sum(r.method == "PUT" for r in transport.requests), 1)
        self.assertIn("uncertain", output.lower())

    def test_redirect_handler_rejects_even_same_host_redirects(self):
        request = card.urllib.request.Request(SOURCE)
        for url in (SOURCE, "https://evil.example/", API):
            with self.subTest(url=url):
                result = card.NoRedirect().redirect_request(request, None, 302, "redirect", {}, url)
                self.assertIsNone(result)


class ValidatorTests(unittest.TestCase):
    def test_valid_graph_preserves_original_bytes(self):
        # Given a static graph for the fixed account, when validated,
        result = card.validate_svg(VALID)
        # Then its exact original bytes survive, without serialization.
        self.assertEqual(result, VALID)

    def test_malformed_or_error_svg_is_rejected(self):
        for body in (b"", b"<html>Error</html>", b"<svg", VALID + b"\xff",
                     VALID.replace(b"UTF-8", b"ISO-8859-1"),
                     VALID.replace(b'version="1.0"', b'broken="declaration"'),
                     VALID.replace(b"Tokens", b"Service unavailable"),
                     VALID.replace(b"<text>Cost</text>", b"<text>Something went wrong</text>"),
                     VALID.replace(b"<g data-contribution-panel=", b"<g data-other=")):
            with self.subTest(body=body[:40]):
                with self.assertRaises(card.CardError):
                    card.validate_svg(body)

    def test_wrong_identity_or_dimensions_are_rejected(self):
        replacements = [(b"@roian6", b"@roian60"), (b"graph", b"compact"),
                        (b'width="680"', b'width="681"'),
                        (b"http://www.w3.org/2000/svg", b"http://example.com/svg")]
        replacements += [(b'height="240"', b'height="' + value + b'"')
                         for value in (b"0", b"-1", b"NaN", b"inf", b"0.01", b"999999")]
        for before, after in replacements:
            with self.subTest(after=after):
                with self.assertRaises(card.CardError):
                    card.validate_svg(VALID.replace(before, after))

    def test_active_content_or_external_references_are_rejected(self):
        additions = [b"<script>alert(1)</script>", b"<foreignObject/>", b"<animate/>",
                     b'<rect onclick="alert(1)"/>', b'<rect ONLOAD="alert(1)"/>',
                     b'<image href="https://example.com/x"/>',
                     b'<rect fill="url(https://example.com/x)"/>',
                     b'<rect style="fill:url(https://example.com/x)"/>',
                     b'<style>@import "https://example.com/x";</style>',
                     b'<style>text{fill:u\\72l(https://example.com/x)}</style>',
                     b'<rect xml:base="https://example.com"/>',
                     b'<g xmlns="http://www.w3.org/1999/xhtml"/>',
                     b'<rect href="data:image/svg+xml;base64,AAAA"/>',
                     b'<style>text{fill:u/**/rl(https://example.com/x)}</style>']
        bodies = [VALID.replace(b"</svg>", addition + b"</svg>") for addition in additions]
        bodies += [b'<!DOCTYPE svg [<!ENTITY x "unsafe">]>' + VALID,
                   b'<?xml-stylesheet href="https://example.com/x"?>' + VALID]
        for body in bodies:
            with self.subTest(body=body[-100:]):
                with self.assertRaises(card.CardError):
                    card.validate_svg(body)

    def test_svg_size_limit_is_enforced(self):
        padded = VALID.replace(b"</svg>", b" " * (256 * 1024 - len(VALID)) + b"</svg>")
        self.assertEqual(card.validate_svg(padded), padded)
        with self.assertRaises(card.CardError):
            card.validate_svg(padded + b" ")


if __name__ == "__main__":
    unittest.main()
