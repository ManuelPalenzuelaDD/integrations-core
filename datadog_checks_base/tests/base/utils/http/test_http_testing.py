# (C) Datadog, Inc. 2026-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import pytest

from datadog_checks.base import AgentCheck
from datadog_checks.base.utils.http_exceptions import HTTPStatusError
from datadog_checks.base.utils.http_testing import MockHTTPResponse


class TestMockHTTPFixture:
    def test_patches_agentcheck_http(self, mock_http):
        check = AgentCheck('test', {}, [{}])
        assert check.http is mock_http


class TestMockHTTPResponseJSON:
    def test_json_with_custom_headers(self):
        headers = {'X-Custom': 'value'}
        response = MockHTTPResponse(json_data={'key': 'value'}, headers=headers)

        assert response.headers['content-type'] == 'application/json'
        assert response.headers['x-custom'] == 'value'

    def test_json_does_not_mutate_caller_headers(self):
        headers = {'X-Custom': 'value'}
        MockHTTPResponse(json_data={'key': 'value'}, headers=headers)

        assert list(headers.keys()) == ['X-Custom']


class TestMockHTTPResponseFilePath:
    def test_file_path_reads_content(self, tmp_path):
        f = tmp_path / 'fixture.txt'
        f.write_bytes(b'file content')

        response = MockHTTPResponse(file_path=str(f))
        assert response.content == b'file content'


class TestMockHTTPResponseStatus:
    def test_raise_for_status(self):
        response_404 = MockHTTPResponse(content='Not Found', status_code=404)
        with pytest.raises(HTTPStatusError) as exc_info:
            response_404.raise_for_status()
        assert '404 Client Error' in str(exc_info.value)
        assert exc_info.value.response is response_404

        response_500 = MockHTTPResponse(content='Server Error', status_code=500)
        with pytest.raises(HTTPStatusError) as exc_info:
            response_500.raise_for_status()
        assert '500 Server Error' in str(exc_info.value)
        assert exc_info.value.response is response_500


class TestMockHTTPResponseStreaming:
    def test_iter_content_chunks_by_size(self):
        response = MockHTTPResponse(content='hello world')

        chunks = list(response.iter_content(chunk_size=5))
        assert chunks == [b'hello', b' worl', b'd']

    def test_iter_lines_preserves_empty_lines(self):
        content = 'line1\n\nline3\n'
        response = MockHTTPResponse(content=content)

        lines = list(response.iter_lines())
        assert lines == [b'line1', b'', b'line3']


class TestMockHTTPResponseNormalization:
    def test_normalize_leading_newline(self):
        content = '\nActual content'
        response = MockHTTPResponse(content=content)

        assert response.text == 'Actual content'
