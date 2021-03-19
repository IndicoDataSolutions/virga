import os
import time
import hmac
import hashlib
import base64
from typing import Optional, Union, Tuple
from http.cookies import _unquote as _unquote_cookie

#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
#
# https://github.com/tornadoweb/tornado/blob/v6.0.4/tornado/web.py
#

_COOKIE_SECRET = os.getenv("ATMOSPHERE_COOKIE_SECRET", "atmospherecookiesecret")


def utf8_bytes(value: Union[str, bytes]) -> bytes:
    return value.encode("utf-8") if isinstance(value, str) else value


def _decode_fields_v2(value: bytes) -> Tuple[bytes, bytes, bytes, bytes]:
    def _consume_field(s: bytes) -> Tuple[bytes, bytes]:
        length, _, rest = s.partition(b":")
        n = int(length)
        field_value = rest[:n]
        # In python 3, indexing bytes returns small integers; we must
        # use a slice to get a byte string as in python 2.
        if rest[n : n + 1] != b"|":
            raise ValueError("malformed v2 signed value field")
        rest = rest[n + 1 :]
        return field_value, rest

    rest = value[2:]  # remove version number
    _, rest = _consume_field(rest)
    timestamp, rest = _consume_field(rest)
    name_field, rest = _consume_field(rest)
    value_field, passed_sig = _consume_field(rest)
    return timestamp, name_field, value_field, passed_sig


def _create_signature_v2(secret: str, s: bytes) -> bytes:
    hash = hmac.new(utf8_bytes(secret), digestmod=hashlib.sha256)
    hash.update(utf8_bytes(s))
    return utf8_bytes(hash.hexdigest())


def _decode_signed_value_v2(name: str, value: bytes, max_age_days) -> Optional[bytes]:
    try:
        timestamp_bytes, name_field, value_field, passed_sig = _decode_fields_v2(value)
    except Exception:
        # Invalid cookie value.
        return None

    signed_string = value[: -len(passed_sig)]
    expected_sig = _create_signature_v2(_COOKIE_SECRET, signed_string)

    if not hmac.compare_digest(passed_sig, expected_sig):
        # The cookie signature is invalid.
        return None
    if name_field != utf8_bytes(name):
        # The cookie name is wrong..
        return None

    timestamp = int(timestamp_bytes)

    if timestamp < time.time() - max_age_days * 86400:
        # The signature has expired.
        return None
    try:
        return base64.b64decode(value_field)
    except Exception:
        return None


def _encode_signed_value_v2(name: str, value: bytes):
    timestamp = utf8_bytes(str(int(time.time())))
    value = base64.b64encode(value)

    def format_field(s: Union[str, bytes]) -> bytes:
        return utf8_bytes("%d:" % len(s)) + utf8_bytes(s)

    to_sign = b"|".join(
        [
            b"2",
            format_field(str(0)),
            format_field(timestamp),
            format_field(name),
            format_field(value),
            b"",
        ]
    )

    signature = _create_signature_v2(_COOKIE_SECRET, to_sign)
    return to_sign + signature


def read_secure_cookie(name: str, value: str, max_age_days: int = 31) -> Optional[str]:
    """
    Decodes a version 2 secure cookie encoded by Atmosphere/Tornado.
    """
    # Cookies may or may not be quoted per RFC 6265
    # https://tools.ietf.org/html/rfc6265#section-4.1.1
    value = _unquote_cookie(value)
    decoded = _decode_signed_value_v2(name, utf8_bytes(value), max_age_days)
    return decoded.decode("utf-8") if isinstance(decoded, bytes) else decoded


def write_secure_cookie(name: str, value: str) -> str:
    """
    Generates a version 2 secure cookie to mimic one encoded by Atmosphere/Tornado.
    """
    return _encode_signed_value_v2(name, utf8_bytes(value)).decode("utf-8")
