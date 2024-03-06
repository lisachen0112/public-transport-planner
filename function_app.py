import azure.functions as func
import logging
import json
import requests

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


def get_tfl_data(departure, arrival, access_params):

    BASE_URL = f"https://api.tfl.gov.uk/journey/journeyresults/{departure}/to/{arrival}"

    response = requests.get(BASE_URL,
                            params={'mode': "walking,tube,bus,dlr,elizabeth-line,overground,tram",
                                    'accessibilityPreference': access_params})
    status = response.status_code
    if status != 200:
        data = response.json()
    else:
        response = response.json()['journeys'][0]
        data = {}
        data['duration'] = response['duration']
        data['legs'] = []
        for leg in response['legs']:
            leg_info = {}
            leg_info['summary'] = leg['instruction']['summary']

            leg_info['departurePoint'] = {'commonName': leg['departurePoint']['commonName'], 
                                          'lat': leg['departurePoint']['lat'], 
                                          'lon': leg['departurePoint']['lon'], 
                                          'platformName': leg['departurePoint']['platformName'] if 'platformName' in leg['departurePoint'] else ""}
            
            leg_info['arrivalPoint'] = {'commonName': leg['arrivalPoint']['commonName'], 
                                        'lat': leg['arrivalPoint']['lat'], 
                                        'lon': leg['arrivalPoint']['lon'], 
                                        'platformName': leg['arrivalPoint']['platformName'] if 'platformName' in leg['arrivalPoint'] else ""}    
            data['legs'].append(leg_info)

            leg_info['path'] = leg['path']["lineString"] if 'path' in leg and 'lineString' in leg['path'] else ""
            leg_info['mode'] = leg['mode']['name'] if 'mode' in leg and 'name' in leg['mode'] else ""

    return data, status


@app.route(route="journey")
def public_transport_planner(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    headers = {
        'Access-Control-Allow-Origin': '*',  # Replace '*' with your allowed domain if applicable
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }

    departure = req.params.get('departure')
    arrival = req.params.get('arrival')
    accessibility_option = req.params.get('accessibility')

    if not departure or not arrival:
        return func.HttpResponse("Please pass a departure and arrival location!", status_code=400)
    else:
        try:
            data, status = get_tfl_data(departure, arrival, accessibility_option)
        except:
            return "Failed to get tfl data", 500
        return func.HttpResponse(json.dumps(data), status_code=status, headers=headers, mimetype="application/json")