import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from env_variables import your_API, from_address, to_addresses, email_password

# from env_variables
myAPI = your_API
host = 'api.etherscan.io'


# function to get token value given contract address, block range, and topic
def get_token_values(from_block, to_block, adrs, topic):
    url = 'https://api.etherscan.io/api?module=logs&action=getLogs&fromBlock={}&toBlock={}&address={}' \
          '&topic0={}&apikey={}'.format(from_block, to_block, adrs, topic, myAPI)
    # print(url)
    page = requests.get(url)
    data = page.json()
    status = data["status"]
    if status == '0':
        print('No transactions found')
        return 0
    token_val = data["result"]
    actual_val = token_val[0]["data"]
    actual_val = int(actual_val, 16) * 10**(-8)
    print(actual_val)
    return actual_val


# function to get contract address from the address that's being monitored
def get_contract_address(address, start_block, end_block):
    url = 'http://api.etherscan.io/api?module=account&action=txlist&address={}' \
      '&startblock={}&endblock={}&sort=asc&apikey={}'.format(address, start_block, end_block, myAPI)
    page = requests.get(url)
    data = page.json()
    status = data["status"]
    if status == '0':
        print('No transactions found')
        return 0
    results = data["result"]
    contract_address = results[0]["to"]
    # print(contract_address)
    return contract_address


# function to send an alert to the desired email addresses
def send_alert(token_value):
    # to and from address from env_variables
    fromaddr = from_address
    toaddres = to_addresses
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    # msg['To'] = toaddr
    msg['Subject'] = "Significant Token Transfer Alert"

    body = "{} tokens were just exchanged.".format(token_value)
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    # password from env_variables
    server.login(fromaddr, email_password)
    text = msg.as_string()
    for email in toaddres:
        msg['To'] = email
        server.sendmail(fromaddr, email, text)
    server.quit()


def main(address_to_monitor, start_block, end_block, topic):
    contract_address = get_contract_address(address_to_monitor, start_block, end_block)
    token_val = get_token_values(start_block, end_block, contract_address, topic)

    if token_val > 200:
        send_alert(token_val)



if __name__ == "__main__":
    main('0x0681d8Db095565FE8A346fA0277bFfdE9C0eDBBF', '5120943', '5120943', '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef')




