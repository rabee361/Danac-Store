from twilio.rest import Client

def send_sms(to, body):
    account_sid = "ACd43dd96f4afcff62fdcd8de1aa6ce246"
    auth_token = "4c6af4599bdba11e2d658961f59d3a0a"
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=body,
        from_='+12059463454',  # Replace with your Twilio number
        to=to
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