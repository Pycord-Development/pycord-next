import pycord


app = pycord.GatewayApp(0, level='DEBUG')


# Connects the bot with the token `token` to the Discord Gateway
app.connect('token')
