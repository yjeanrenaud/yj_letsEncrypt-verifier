#!/usr/bin/env python3
##
# checks domains (hostnames or IP-Addresses) for tls certificates and if they expire in three days or less, it sens out an end-to-end-encrypted Message via Threema.
# https://github.com/yjeanrenaud/yj_letsEncrypt-verifier/tree/main
# 2025, Yves Jeanrenaud
## 

import ssl
import socket
import datetime
import asyncio
import logbook
import logbook.more

from threema.gateway import (
    Connection,
    GatewayError,
    util,
)
from threema.gateway.e2e import TextMessage

## FILL in the Threema-ID of the recipient
threemaRcptID = "THREEMA_ID"
## FILL in your crdentials
threemaGatewayID = "*GATEWAY_ID"
threemaSecret = "MY_SECRET"
threemaPrivateKey="private:MY_PRIVATE_KEY"

# List of domains to check
## FILL in your domains and/or hosts to check
domains = [
    "some.domain.to.check",
    "127.0.0.1"
    # Add more domains or hosts as needed
]

async def get_cert_expiration_date(host, port=443):
    """
    Connects to the host and retrieves the TLS certificate expiration date.
    """
    context = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=5) as sock:
        with context.wrap_socket(sock, server_hostname=host) as ssock:
            cert = ssock.getpeercert()
    # The certificate's 'notAfter' field is a string like 'Jun  8 12:00:00 2023 GMT'
    not_after = cert.get('notAfter')
    if not not_after:
        raise ValueError("No 'notAfter' field in certificate")
    # Convert the expiration date to a datetime object
    expiration_date = datetime.datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
    return expiration_date

async def check_cert(host, port=443):
    """
    Checks the certificate for the given host and returns the days remaining.
    """
    expiration_date = await get_cert_expiration_date(host, port)
    now =  datetime.datetime.utcnow()
    # Calculate the total remaining time in days (can be fractional)
    remaining = (expiration_date - now).total_seconds() / 86400
    return remaining, expiration_date

async def send_alert(domain, days_left, expiration_date, toID):
    """
    Sends a notification alert using the Threema API.
    """
    connection = Connection(
        identity=threemaGatewayID,
        secret=threemaSecret,
        key=threemaPrivateKey,
    )
    message = TextMessage( 
        connection=connection,
        to_id=toID,
        text=f"TLS certificate for {domain} expires in {days_left:.1f} days {expiration_date}."
    )
    try:
      async with connection: 
        await message.send()
        print(f"sending Alert: \n{message}") 
    except Exception as e:
      print(f"Error ending alter for {domain}: {e}")

async def main():
    for domain in domains:
        try:
            days_left, expiration_date = await check_cert(domain)
            if days_left <= 3:
                await send_alert(domain, days_left, expiration_date, threemaRcptID)
                print(f"Alert sent for {domain}: Certificate expires in {days_left:.1f} days.")
            else:
                print(f"{domain}: Certificate valid for {days_left:.1f} days.")
        except Exception as e:
            print(f"Error checking certificate for {domain}: {e}")
    
if __name__ == '__main__':
    util.enable_logging(logbook.WARNING)
    log_handler = logbook.more.ColorizedStderrHandler()
    with log_handler.applicationbound():
        asyncio.run(main())
