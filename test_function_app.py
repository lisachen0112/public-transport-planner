import pytest
from unittest.mock import patch
from function_app import get_tfl_data, main
import azure.functions as func


@patch('requests.get')
def test_get_tfl_data_success(mock_requests_get):
    # Mock the response from the API
    mock_response = {
        'journeys': [
            {
                'duration': 30,
                'legs': [
                    {
                        'instruction': {'summary': 'Walk to the station'},
                        'departurePoint': {'commonName': 'Start Station', 'lat': 12.34, 'lon': 56.78, 'platformName': 'A'},
                        'arrivalPoint': {'commonName': 'End Station', 'lat': 23.45, 'lon': 67.89, 'platformName': 'B'},
                        'path': '',
                        'mode': ''
                    }
                ]
            }
        ]
    }
    mock_requests_get.return_value.json.return_value = mock_response
    mock_requests_get.return_value.status_code = 200

    # Call the function with mock data
    result, status = get_tfl_data('start', 'end')

    # Assert the expected result
    expected_result = {
        'duration': 30,
        'legs': [
            {
                'summary': 'Walk to the station',
                'departurePoint': {'commonName': 'Start Station', 'lat': 12.34, 'lon': 56.78, 'platformName': 'A'},
                'arrivalPoint': {'commonName': 'End Station', 'lat': 23.45, 'lon': 67.89, 'platformName': 'B'},
                'path': '',
                'mode': ''
            }
        ]
    }
    assert result == expected_result
    assert status == 200


@patch('requests.get')
def test_get_tfl_data_failure(mock_requests_get):
    # Mock a failed response from the API
    mock_requests_get.return_value.status_code = 404

    # Call the function with mock data and assert the exception
    with pytest.raises(Exception, match="Failed to get data: 404"):
        result, status = get_tfl_data('start', 'end')


def test_success_endpoint():
    # Construct a mock HTTP request.
    req = func.HttpRequest(method='GET',
                           body=None,
                           url='/api/journey',
                           params={'departure': 'w36ad',
                                   'arrival': 'sw72az'})
    # Call the function.
    func_call = main.build().get_user_function()
    resp = func_call(req)
    # Check the output.
    assert resp.status_code == 200


def test_fail_endpoint():
    # Construct a mock HTTP request.
    req = func.HttpRequest(method='GET',
                           body=None,
                           url='/api/journey')
    # Call the function.
    func_call = main.build().get_user_function()
    resp = func_call(req)
    # Check the output.
    assert resp.status_code == 400
