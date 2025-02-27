# yj_letsEncrypt-verifier
As LetsEncrypt discontinues their e-mail warning for expiring certificates, I wrote something to check my own. Exisiting solutions often require that the hosts are reachable from the internet, which is someting I do not have for all certificates I use. 
(Yes, I tls-encrypt traffic in my own private network, too, by manipulating my own dns servers tables to have FQDN resolved locally, too. Like that, I can use services that depend on encrypted transmissions with the same easy from within and beyond my reverse proxy).

## prerequisites and dependencies
- you need to set up a threema gateway account and have some credits balance on it. see [https://gateway.threema.ch](https://gateway.threema.ch) for this. See [threema-msgapi-sdk-python](https://github.com/threema-ch/threema-msgapi-sdk-python/) for details.
- you need a Threema ID where you want to receive the alerts to
- python3 `sudo apt-get update;sudo apt-get install python3`
- python threema-msgapi-sdk: `pip install threema.gateway`
- python libraries: socket, asyncio and logbook: `pip install socket asyncio logbook`
# setup and usage
- copy [tls_check_threema.py](https://github.com/yjeanrenaud/yj_letsEncrypt-verifier/blob/main/tls_check_threema.py) to a secure folder and make it executeable `chmod a+x tls_check_threema.py`
- fill in your detials:
  - **threemaRcptID** with the Threema ID that shall receive alerts. It is usually eight characters long.
  - **threemaGatewayID** with the Threema ID of your gateway. It usually starts with a * and seven charakters.
  - **threemaSecret** contains the secret of your gateway. You can see it when you log into [gateway.threema.ch](https://gateway.threema.ch).
  - **threemaPrivateKey** is your gateway's private key. it must be a hex formated string and prefixed with *private:*.
    You generated it while setting up your gateway. If not, see [https://gateway.threema.ch/en/developer/howto/create-keys/python ](https://gateway.threema.ch/en/developer/howto/create-keys/python) for how to. But it's pretty straight forwared: `threema-gateway generate privateKey.txt publicKey.txt`
  - specifiy one or more domains/hosts to check in **domains** = []

- test your credentials:
    `threema-gateway send-e2e [RCPT_ID] [*GATEWAY_ID] [SECRET] "private:PRIVATE_KEY" "This is a test"`.
     optionally, you may also add a line to the python file: `await send_alert("FAKE.DOMAIN.EXAMPLE", 2, "01.03.2025", threemaRcptID)` within `main()`. Be sure to remove/comment that line after your initial test run (`./tls_check_threema.py`)
- set up a cronjob for regular checks on your domains tls certificates:
  e.g. `cron -e` and insert the line `11 5 * * * /usr/bin/enc python3 /path/to/tls_check_threema.py` so every day at 11:05 am, the checking is done.

# Todos
- secure the credentials
- harden code
