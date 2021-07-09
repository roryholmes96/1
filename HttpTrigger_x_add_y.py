from requests_futures.sessions import FuturesSession

session = FuturesSession()

x=30
y=84
x2=10
y2=32

future_one = session.get(f'https://r96-httptrigger-x-add-y.azurewebsites.net/api/HttpTrigger_x_add_y?x={x}&y={y}')

future_two = session.get(f'https://r96-httptrigger-x-add-y.azurewebsites.net/api/HttpTrigger_x_add_y?x={x2}&y={y2}')

future_three = session.get(f'https://r96-httptrigger-x-add-y.azurewebsites.net/api/HttpTrigger_x_add_y?x={x2}&y={y}')

future_four = session.get(f'https://r96-httptrigger-x-add-y.azurewebsites.net/api/HttpTrigger_x_add_y?x={x}&y={y2}')

response_one = future_one.result()
print(response_one.text)

response_two = future_two.result()
print(response_two.text)

response_three = future_three.result()
print(response_three.text)

response_four = future_four.result()
print(response_four.text)
