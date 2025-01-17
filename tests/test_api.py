import os
import socket
from http import HTTPMethod
from string import printable
from typing import Any

import pytest
import requests
from hypothesis import given
from hypothesis import strategies as st

from mock.models import Dashboard, Error, GetDashboardPostRequest, GetDashboardsPostRequest, GetDashboardsPostResponse

API_HOST = os.environ["ELM_BI_API_HOST"]
API_PORT = int(os.environ["ELM_BI_API_PORT"])
API_URL = f"http://{API_HOST}:{API_PORT}"

SUPPORTED_METHODS = {HTTPMethod.OPTIONS, HTTPMethod.POST}
UNSUPPORTED_METHODS = set(HTTPMethod) - SUPPORTED_METHODS

JSON_CHARS = set(printable + "\b") - {"\v"}


json_strategy = st.one_of(
    st.dictionaries(st.text(JSON_CHARS), st.text(JSON_CHARS), min_size=1),
    st.lists(st.text(JSON_CHARS)),
    st.text(JSON_CHARS),
    st.integers(),
)


def test_options():
    """Given OPTIONS request.

    Server must respond with empty body and proper CORS headers.
    """
    response = requests.options(f"{API_URL}/")
    assert response.status_code == 204
    assert response.headers.get("Content-Type") == "application/json"
    assert response.headers.get("Connection") == "close"
    assert response.headers.get("Access-Control-Allow-Origin") == "*"


@pytest.mark.parametrize(
    argnames=["method"],
    argvalues=[(method,) for method in UNSUPPORTED_METHODS],
)
def test_unsupported_method(method: HTTPMethod):
    """Given HTTP method other than OPTIONS or POST.

    Server must respond with Method Not Allowed status code.
    """
    response = requests.request(method, f"{API_URL}/")
    assert response.status_code == 405


# @example("")
@given(st.text(min_size=1))
def test_malformed_http_request(data: str):
    """Given malformed http request.

    Server must close the connection.

    It is known, but yet not fixed bug: empty request body make server hang forever.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((API_HOST, API_PORT))
        s.sendall(data.encode())
        s.recv(4096)


def test_action_body_not_json():
    """Given action (POST) request without Content-Type: application/json.

    Server must respond with Unsupported Media Type status code.
    """
    response = requests.post(f"{API_URL}/get-dashboards", data="not a json")
    assert response.status_code == 415


def test_action_body_invalid_json():
    """Given action (POST) request with invalid JSON data.

    Server must respond with Bad Request status code and error details.
    """
    response = requests.post(
        f"{API_URL}/get-dashboards",
        data="not a json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400
    Error.model_validate_json(response.text)


@given(st.builds(GetDashboardsPostRequest))
def test_get_dashboards_valid(request: GetDashboardsPostRequest):
    """Given valid /get-dashboards request.

    Server must respond with list of dashboards.
    """
    response = requests.post(f"{API_URL}/get-dashboards", json=request.model_dump())
    GetDashboardsPostResponse.model_validate_json(response.text)


@given(json_strategy)
def test_get_dashboards_invalid(request: Any):
    """Given invalid /get-dashboards request.

    Server must respond with Unprocessable Content status code and expected format details.

    It is known issue that server JSON decoder does not support all possible Uncode characters.
    """
    response = requests.post(f"{API_URL}/get-dashboards", json=request)
    assert response.status_code == 422
    Error.model_validate_json(response.text)


@given(st.builds(GetDashboardPostRequest))
def test_get_dashboard_valid(request: GetDashboardPostRequest):
    """Given valid /get-dashboard request.

    Server must respond with dashboard or Not Found status code.
    """
    response = requests.post(f"{API_URL}/get-dashboard", json=request.model_dump())
    assert response.status_code in {200, 404}
    if response.status_code == 200:
        Dashboard.model_validate_json(response.text)


@given(json_strategy)
def test_get_dashboard_invalid(request: Any):
    """Given invalid /get-dashboard request.

    Server must respond with Unprocessable Content status code and expected format details.
    """
    response = requests.post(f"{API_URL}/get-dashboard", json=request)
    assert response.status_code == 422
    Error.model_validate_json(response.text)
