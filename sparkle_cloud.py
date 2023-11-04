import asyncio
import random
import time
import datetime
import aiohttp
import json
import colorama
from colorama import Fore, Back, Style
from discord_webhook import DiscordWebhook, DiscordEmbed

# Constants
json_file = 'tasks.json'
public_success_webhook = DiscordWebhook(url='https://discord.com/api/webhooks/.....', rate_limit_retry=True, username="SPARKLE|PUBLIC")
public_failures_webhook = DiscordWebhook(url='https://discord.com/api/webhooks/.....', rate_limit_retry=True, username="SPARKLE|PUBLIC")
boss_hook = DiscordWebhook(url='https://discord.com/api/webhooks/.....', rate_limit_retry=True, username="SPARKLE")
version = 'v 1.2'
url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"


colorama.init()

# Load JSON data from a file
with open(json_file) as f:
    js = json.loads(f.read())

# Prepare headers and proxies
h = {
    "authority": "www.binance.com",
    "accept": "*/*",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "bnc-location": "BINANCE",
    "clienttype": "web",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
}
proxies = []
webhook_responses = []
count = 0
order_request_sent = False

# Extract and organize proxies from JSON data
for user_id, user_data in js.items():
    try:
        user_proxies = user_data.get("proxy", [])
        pro = []
        for p in user_proxies:
            pr = p.split(':')
            ip = pr[0]
            port = pr[1]
            try:
                login = pr[2]
                pas = pr[3]
                user_proxy = f'http://{login}:{pas}@{ip}:{port}'
            except:
                user_proxy = f'http://{ip}:{port}'

            if js[user_id]["tasks_running"] != False:
                proxies.append(user_proxy)
            pro.append(user_proxy)
        js[user_id]["proxy"] = pro
    except Exception as e:
        print(e)

print('Proxies: ' + str(len(proxies)))

# Define an async function to send order requests
async def send_order_request(session, payload, response, user):
    global order_request_sent, webhook_responses, count

    times = time.time()
    prox = random.choice(user[1]["proxy"])

    try:
        async with session.post(
                'https://p2p.binance.com/bapi/c2c/v2/private/c2c/order-match/makeOrder',
                headers=user[1]["headers"],
                cookies=user[1]["cookies"],
                json=payload,
                proxy=prox,
                timeout=60) as order_response:

            resp = await order_response.json()

            checkout_time = time.time() - times

            print(str(datetime.datetime.now()) + '----' + str(resp))
            print(checkout_time)
            if resp['success']:
                print(str(datetime.datetime.now()) + Fore.GREEN + '---SUCCESS---' + Style.RESET_ALL)

                webhook_responses.append({
                    'success': True,
                    's_hook_link': user[1]["success_webhook"],
                    'proxy': prox,
                    'username': user[0],
                    'sum': f'{payload["totalAmount"]} Руб',
                    'checkout_time': checkout_time,
                    'diff': f'{float(response["data"][1]["adv"]["price"]) - float(response["data"][0]["adv"]["price"])} Руб',
                    'limits': f'{response["data"][0]["adv"]["minSingleTransAmount"]}-{response["data"][0]["adv"]["dynamicMaxSingleTransAmount"]} Руб',
                    'payment': response["data"][0]["adv"]["tradeMethods"][0]["tradeMethodName"],
                    'buy_offer': f'{response["data"][0]["adv"]["price"]}/{response["data"][1]["adv"]["price"]}'
                })
            else:
                webhook_responses.append({
                    'success': False,
                    'f_hook_link': user[1]["failure_webhook"],
                    'proxy': prox,
                    'username': user[0],
                    'sum': f'{payload["totalAmount"]} Рub',
                    'checkout_time': checkout_time,
                    'diff': f'{float(response["data"][1]["adv"]["price"]) - float(response["data"][0]["adv"]["price"])} Руб',
                    'limits': f'{response["data"][0]["adv"]["minSingleTransAmount"]}-{response["data"][0]["adv"]["dynamicMaxSingleTransAmount"]} Руб',
                    'payment': response["data"][0]["adv"]["tradeMethods"][0]["tradeMethodName"],
                    'reason': resp["message"],
                    'buy_offer': f'{response["data"][0]["adv"]["price"]}/{response["data"][1]["adv"]["price"]}'
                })
    except Exception as e:
        print(e)
        embed_failure = DiscordEmbed(title='ERROR WHILE CHECKING OUT',
                                     description=str(e),
                                     color='FF0000')
        embed_failure.set_thumbnail(url='https://i.ibb.co/HX0YBLT/logo2.png')

        embed_failure.set_footer(text=f'SPARKLE --{version}--')
        boss_hook.remove_embeds()
        boss_hook.add_embed(embed_failure)
        boss_hook.execute()
        embed_failure = DiscordEmbed(title='ERROR WHILE CHECKING OUT',
                                     description=str(resp),
                                     color='FF0000')
        embed_failure.set_thumbnail(url='https://i.ibb.co/HX0YBLT/logo2.png')

        embed_failure.set_footer(text=f'SPARKLE --{version}--')
        boss_hook.remove_embeds()
        boss_hook.add_embed(embed_failure)
        boss_hook.execute()
        print(e)
    finally:
        await asyncio.sleep(5)
        count += 1
        webhook()
        order_request_sent = False

# Define a function to send webhooks
def webhook():
    if count == 1:
        print('calling')
        for response in webhook_responses:
            try:
                if response['success']:
                    embed_success = DiscordEmbed(title='Successful deal',
                                                 url='https://p2p.binance.com/ru/fiatOrder?tab=1&page=1',
                                                 color='00ff00')
                    embed_success.set_thumbnail(url='https://i.ibb.co/HX0YBLT/logo2.png')
                    embed_success.add_embed_field(name='Currency:', value='USDT')
                    embed_success.add_embed_field(name='Buy offer:', value=response['buy_offer'])
                    embed_success.add_embed_field(name='Difference:', value=response['diff'])
                    embed_success.add_embed_field(name='Sum:', value=response['sum'])
                    embed_success.add_embed_field(name='Limits:', value=response['limits'])
                    embed_success.add_embed_field(name='Payment method:', value=response['payment'])
                    embed_success.add_embed_field(name='Proxy:', value=f'||{response["proxy"]}||')
                    embed_success.add_embed_field(name='Links',
                                                 value='[p2p](https://p2p.binance.com/ru/trade/TinkoffNew/USDT?fiat=RUB) | [Notifications](https://www.binance.com/ru/inmail)')
                    embed_success.add_embed_field(name='Checkout time',
                                                 value=f'{response["checkout_time"]} seconds')
                    embed_success.set_footer(text=f'SPARKLE --{version}--')
                    s_hook = DiscordWebhook(url=response['s_hook_link'], rate_limit_retry=True, username="SPARKLE")
                    s_hook.remove_embeds()
                    s_hook.add_embed(embed_success)
                    s_hook.execute()
                    public_success_webhook.remove_embeds()
                    embed_success.add_embed_field(name='User', value=str(response['username']))
                    public_success_webhook.add_embed(embed_success)
                    public_success_webhook.execute()
                else:
                    print(str(datetime.datetime.now()) + Fore.RED + '---FAILURE---' + Style.RESET_ALL)
                    embed_failure = DiscordEmbed(title='Failure',
                                                 url='https://p2p.binance.com/ru/fiatOrder?tab=1&page=1',
                                                 color='FF0000')
                    embed_failure.set_thumbnail(url='https://i.ibb.co/HX0YBLT/logo2.png')
                    embed_failure.add_embed_field(name='Currency:', value='USDT')
                    embed_failure.add_embed_field(name='Buy offer:', value=response['buy_offer'])
                    embed_failure.add_embed_field(name='Difference:', value=response['diff'])
                    embed_failure.add_embed_field(name='Sum:', value=response['sum'])
                    embed_failure.add_embed_field(name='Limits:', value=response['limits'])
                    embed_failure.add_embed_field(name='Payment method:', value=response['payment'])
                    embed_failure.add_embed_field(name='Reason:', value=response['reason'])
                    embed_failure.add_embed_field(name='Proxy:', value=f'||{response["proxy"]}||')
                    embed_failure.add_embed_field(name='Links',
                                                 value='[p2p](https://p2p.binance.com/ru/trade/TinkoffNew/USDT?fiat=RUB) | [Notifications](https://www.binance.com/ru/inmail)')
                    embed_failure.add_embed_field(name='Checkout time',
                                                 value=f'{response["checkout_time"]} seconds')
                    embed_failure.set_footer(text=f'SPARKLE --{version}--')
                    f_hook = DiscordWebhook(url=response['f_hook_link'], rate_limit_retry=True, username="SPARKLE")
                    f_hook.remove_embeds()
                    f_hook.add_embed(embed_failure)
                    f_hook.execute()
                    public_failures_webhook.remove_embeds()
                    embed_failure.add_embed_field(name='User', value=str(response['username']))
                    public_failures_webhook.add_embed(embed_failure)
                    public_failures_webhook.execute()
            except Exception as e:
                print(e)

# Define an async function to send HTTP requests
async def send_request(session, json_data_buy):
    global order_request_sent, webhook_responses, count

    while True:
        proxy = random.choice(proxies)

        try:
            async with session.post(url, json=json_data_buy, proxy=proxy, timeout=99999999, headers=h) as response:
                if not order_request_sent:
                    try:
                        response = await response.json()
                        print(str(datetime.datetime.now()) + '---' + "[" + json_data_buy['asset'] + ']' + '---' + response['data'][0]['adv']['price'] + '/' + response['data'][1]['adv']['price'])

                        for user in js.items():
                            for task_ in user[1]["tasks"]:
                                for pm in response['data'][0]['adv']['tradeMethods']:
                                    if (float(response['data'][1]['adv']['price']) - float(response['data'][0]['adv']['price']) >= float(task_['minimum_diff']) and
                                            float(response['data'][0]['adv']['minSingleTransAmount']) <= float(task_["maximum_sum"]) and
                                            float(response['data'][0]['adv']['dynamicMaxSingleTransAmount']) >= float(task_["minimum_sum"]) and
                                            pm["identifier"] in task_["payment_methods"] and
                                            user[1]["tasks_running"]):
                                        ORDER_PAYLOAD = {
                                            'advOrderNumber': response['data'][0]['adv']['advNo'],
                                            'asset': json_data_buy['asset'],
                                            'matchPrice': response['data'][0]['adv']['price'],
                                            'fiatUnit': 'RUB',
                                            'buyType': 'BY_MONEY',
                                            'totalAmount': float(task_["maximum_sum"]),
                                            'tradeType': 'BUY',
                                            'origin': 'MAKE_TAKE'
                                        }
                                        ORDER_PAYLOAD_1 = {
                                            'advOrderNumber': response['data'][0]['adv']['advNo'],
                                            'asset': json_data_buy['asset'],
                                            'matchPrice': response['data'][0]['adv']['price'],
                                            'fiatUnit': 'RUB',
                                            'buyType': 'BY_MONEY',
                                            'totalAmount': response['data'][0]['adv']['dynamicMaxSingleTransAmount'],
                                            'tradeType': 'BUY',
                                            'origin': 'MAKE_TAKE'
                                        }
                                        order_request_sent = True
                                        count = 0
                                        webhook_responses = []
                                        if float(task_["maximum_sum"]) >= float(response['data'][0]['adv']['dynamicMaxSingleTransAmount']):
                                            asyncio.create_task(send_order_request(session, ORDER_PAYLOAD_1, response, user))
                                        else:
                                            asyncio.create_task(send_order_request(session, ORDER_PAYLOAD, response, user))
                                        print(str(datetime.datetime.now()) + '---TASK CREATED')
                    except Exception as e:
                        print(e)
        except Exception as e:
            print(e)

# Define the main asynchronous function
async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for x in range(len(proxies) // 12):
            json_data_buy = {
                'proMerchantAds': False,
                'page': 1,
                'rows': 2,
                'payTypes': ["TinkoffNew", "RosBankNew", "RaiffeisenBank", "QIWI", "MTSBank", "RussianStandardBank",
                             "PostBankNew", "YandexMoneyNew", "HomeCreditBank", "BCSBank", "BankSaintPetersburg",
                             "CitibankRussia", "RaiffeisenBankAval"],
                'countries': [],
                'publisherType': None,
                'asset': 'USDT',
                'fiat': 'RUB',
                'tradeType': 'BUY',
            }
            task = asyncio.create_task(send_request(session, json_data_buy))
            tasks.append(task)
        await asyncio.gather(*tasks)

# Run the main asynchronous function
asyncio.run(main())
