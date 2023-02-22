import alpaca_trade_api as tradeapi
import os

from discord import send_discord_message

# set up your env variables
API_KEY = os.getenv('ALPACA_API_KEY')
SECRET_KEY = os.getenv('ALPACA_SECRET')
BASE_URL = os.getenv('ALPACA_ENDPOINT')
STOCK_SYMBOL = os.getenv('STOCK_SYMBOL')

# connect to the Alpaca API
api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

# get current position
def get_current_position():
    shares_held_currently = 0
    portfolio = api.list_positions()    
    for position in portfolio:
        if position.symbol == STOCK_SYMBOL:
            shares_held_currently = position.qty
    return shares_held_currently

# get latest price
def get_last_price():
    last_price_raw = api.get_latest_quote(STOCK_SYMBOL)
    last_price = last_price_raw.ap

    return last_price

# place a market buy/sell order
def place_trade_order(signal, last_price):
    discord_message_subj = ':money_with_wings: BOUGHT' if signal == 'buy' else ':moneybag: SOLD'    
    qty = 0    
    account = api.get_account()

    # exit early if trading is blocked on the account
    if account.trading_blocked:
        send_discord_message(f'**BLOCKED**: Trading is currently unavailable')
        return
    
    # exit early if half of buying power wouldn't be enough to buy a single share
    if float(account.buying_power)/2 < last_price:
        send_discord_message(f':skull_crossbones: **BROKE ASS**: Not enough buying power to satisfy rules')

    # get a list of all of our positions to set shares_held_currently
    shares_held_currently = get_current_position()

    # for sell orders, we want to sell all owned shares, for buys we set that in the env variables
    if signal == 'sell':
        qty = shares_held_currently
    else:
        # for buy orders we want to buy for no more than half of what our current buying power allows
        qty = int((float(account.buying_power)/2)/float(151.38))
    
    if qty > 0:
        try:
            send_discord_message(f':rocket: Currently holding {shares_held_currently} {STOCK_SYMBOL} share/s')
            api.submit_order(
                symbol=STOCK_SYMBOL,
                qty=qty,
                side=signal,
                type='market',
                time_in_force='gtc'
            )
            send_discord_message(f'**{discord_message_subj}** {qty} {STOCK_SYMBOL} share/s at +-${last_price:.2f}')
        except:            
            send_discord_message(f':sob: **FAILED**{signal}: Check logs for details')
    else:
        if signal == 'sell':
            send_discord_message(f':pinching_hand: **NO POSITIONS**: Can\'t sell what you don\'t have')