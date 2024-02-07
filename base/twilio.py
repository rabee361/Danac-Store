# # Download the helper library from https://www.twilio.com/docs/python/install
# import os
# import twilio
# from twilio.rest import Client

# # Set environment variables for your credentials
# # Read more at http://twil.io/secure
account_sid = "ACd43dd96f4afcff62fdcd8de1aa6ce246"
auth_token = "8e4f804654eef544401e843ed5d0365a"
# verify_sid = "VAd362316a9d9009f6fa9ee31873920036"
# verified_number = "+213660030002"

# client = Client(account_sid, auth_token)

# verification = client.verify.v2.services(verify_sid) \
#   .verifications \
#   .create(to=verified_number, channel="sms")
# print(verification.status)

# otp_code = input("Please enter the OTP:")

# verification_check = client.verify.v2.services(verify_sid) \
#   .verification_checks \
#   .create(to=verified_number, code=otp_code)
# print(verification_check.status)


import twilio
import twilio.rest

try:
    client = twilio.rest.TwilioRestClient(account_sid, auth_token)

    message = client.messages.create(
        body="Hello World",
        to="+14159352345",
        from_="+12059463454"
    )
except twilio.TwilioRestException as e:
    print (e)