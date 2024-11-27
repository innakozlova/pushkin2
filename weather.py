import requests
city = input('City?')
api_url = 'https://api.openweathermap.org/data/2.5/weather'

params = {
    'q': city, #'Saint Petersburg',
    'appid': '6fc4874fe81dae6df599a4618633703b',
    'units': 'metric'

}

res = requests.get(api_url, params = params)
#print(res.status_code)
#print(res.headers['Content-Type'])
#print(res.json())
data = res.json()
template = 'Current temperature in {} is {}'
print(template.format (city, data['main']['temp']))