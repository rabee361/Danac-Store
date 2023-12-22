from twilio.rest import Client

def send_sms(to, body):
    account_sid = "ACd43dd96f4afcff62fdcd8de1aa6ce246"
    auth_token = "8e4f804654eef544401e843ed5d0365a"
    verify_sid = "VAf1969a8852bac9bde1818fd4913f0bea"
    client = Client(account_sid, auth_token)

    # verification = client.verify.v2.services(verify_sid) \
    # .verifications \
    # .create(to=verified_number, channel="sms")
    message = client.messages.create(
        body=body,
        from_='+12059463454',  # Replace with your Twilio number
        to=to,
        
    )

    return message.sid


# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView

# class RegisterView(APIView):
#     def post(self, request, format=None):
#         # Registration logic here...

#         # Send SMS
#         phone_number = request.data.get('phone_number')
#         sms_body = "Thank you for registering!"
#         send_sms(phone_number, sms_body)

#         return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)