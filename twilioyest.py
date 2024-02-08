from twilio.rest import Client

account_sid = 'ACff3b87ddef71a06732596514466ccedd'
auth_token = '8df9fb1e86872f3669442c39bb0a35fd'
client = Client(account_sid, auth_token)

message = client.messages.create(
  from_='+12244125106',
  body='test',
  to='+18777804236'
)

print(message.sid)