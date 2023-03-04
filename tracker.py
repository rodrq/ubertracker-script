import requests
import json
import schedule
import pandas as pd
import config
import time
from datetime import datetime, timedelta

def get_price():
    url = "https://m.uber.com/graphql"
    payload = json.dumps({
        "operationName": "Products",
        "variables": {
            "includeClassificationFilters": False,
            "destinations": config.destino,
            "fallbackTimezone": config.timezone,
            "pickup": config.pickup,
            "targetProductType": None
        },
        "query": "query Products($destinations: [InputCoordinate!]!, $fallbackTimezone: String, $includeClassificationFilters: Boolean = false, $pickup: InputCoordinate!, $pickupFormattedTime: String, $targetProductType: EnumRVWebCommonTargetProductType) {\n  products(\n    destinations: $destinations\n    fallbackTimezone: $fallbackTimezone\n    includeClassificationFilters: $includeClassificationFilters\n    pickup: $pickup\n    pickupFormattedTime: $pickupFormattedTime\n    targetProductType: $targetProductType\n  ) {\n    ...ProductsFragment\n    __typename\n  }\n}\n\nfragment ProductsFragment on RVWebCommonProductsResponse {\n  classificationFilters {\n    ...ClassificationFiltersFragment\n    __typename\n  }\n  defaultVVID\n  productsUnavailableMessage\n  renderRankingInformation\n  tiers {\n    ...TierFragment\n    __typename\n  }\n  __typename\n}\n\nfragment ClassificationFiltersFragment on RVWebCommonClassificationFilters {\n  filters {\n    ...ClassificationFilterFragment\n    __typename\n  }\n  hiddenVVIDs\n  standardProductVVID\n  __typename\n}\n\nfragment ClassificationFilterFragment on RVWebCommonClassificationFilter {\n  currencyCode\n  displayText\n  fareDifference\n  icon\n  vvid\n  __typename\n}\n\nfragment TierFragment on RVWebCommonProductTier {\n  products {\n    ...ProductFragment\n    __typename\n  }\n  title\n  __typename\n}\n\nfragment ProductFragment on RVWebCommonProduct {\n  capacity\n  cityID\n  currencyCode\n  description\n  detailedDescription\n  discountPrimary\n  displayName\n  estimatedTripTime\n  etaStringShort\n  fare\n  hasPromo\n  hasRidePass\n  id\n  isAvailable\n  meta\n  preAdjustmentValue\n  productImageUrl\n  productUuid\n  reserveEnabled\n  __typename\n}\n"
    })
    headers = {
        'accept': '*/*',
        'cookie': config.sid + config.csid,
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'x-csrf-token': 'x',
    }
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        fare = json.loads(response.text)['data']['products']['tiers'][0]['products'][0]['fare'][4:]
        return fare
    except:
        return 'Request error'

def main():
    csvfile = f"data/{datetime.now().strftime('%Y-%m-%d')}.csv"
    try: 
        df = pd.read_csv(csvfile)
    except:
        df = pd.DataFrame(columns=['Hour', 'Price'])
        df.to_csv((csvfile), mode='w', header=True, index=False)

    ### This fills empty cells if the script wasn't online before.  

    try:
        last_row = df.iloc[-1]['Hour'] 
    except IndexError:
        last_row = None
        print('Started new day .csv')
    else:
        last_row = df.iloc[-1]['Hour'] 

    if (datetime.now() - timedelta(minutes=1)).strftime('%H:%M') != last_row:
        for i in range(60*24):
            hour, minute = divmod(i, 60)
            hour_str = f"{hour:02d}"
            minute_str = f"{minute:02d}"
            timestamp_str = f"{hour_str}:{minute_str}"
            if timestamp_str == datetime.now().strftime('%H:%M'):
                break
            if df[df['Hour'] == timestamp_str].empty:
                new_row = {'Hour': timestamp_str, 'Price': 'Script was offline'}
                print(f'{timestamp_str} filled with empty')
                df.loc[len(df)] = new_row
    new_row = {'Hour':datetime.now().strftime('%H:%M'), 'Price': get_price()}
    df.loc[len(df)] = new_row
    df.to_csv(csvfile, mode='w', header=True, index=False)
    print(new_row)

schedule.every(config.interval).minutes.at(":00").do(main)
while True:
    schedule.run_pending()
    time.sleep(1)

