import requests
from datetime import datetime
import json
import time
import schedule
import csv
import os
import config

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

csvfile = 'data/' + 'UberX ' + datetime.now().strftime("%d %m %Y") + '.csv'



def offline_row_filler():
    hour = datetime.now().strftime("%H:%M")
    with open(csvfile, "r") as f:
        last_line = f.readlines()[-1]
        last_csv_hour = last_line[:5]
        try:
            if last_csv_hour != hour:
                total_mins_diff = ((int(hour[:2]) - int(last_csv_hour[:2])) * 60) + (int(hour[3:]) - int(last_csv_hour[3:]))
                hours_added = 0
                with open(csvfile, "a", newline='') as f:
                        for n in range(total_mins_diff-1):
                            n+=1
                            iter_mins = int(last_csv_hour[3:]) + n
                            iter_hour = int(last_csv_hour[:2])
                            if iter_mins >= 60:
                                if iter_mins % 60 == 0:
                                    hours_added += 1
                            iter_mins = iter_mins % 60
                            iter_hour = int(last_csv_hour[:2]) + hours_added
                            if iter_mins < 10:
                                iter_mins = '0' + str(iter_mins)
                            else:
                                iter_mins = str(iter_mins)
                            if iter_hour < 10:
                                iter_hour = '0' + str(iter_hour)
                            else:
                                iter_hour = str(iter_hour)
                            to_cvs_hour = iter_hour + ':' + iter_mins
                            writer = csv.writer(f)
                            writer.writerow([to_cvs_hour, "Sin datos: Script offline"])
                        print('Funcion offline_row_filler() usada')
        except:
            print('Rellenando desde las 00:00')
            with open(csvfile, "r") as f:
                last_line = f.readlines()[-1]
                last_csv_hour = last_line[:5]
                diff = (int(hour[:2]) * 60) + int(hour[3:])
                hours_added = 0
                with open(csvfile, "a", newline='') as f:
                    for n in range(diff-1):
                        n+=1
                        iter_mins = 0 + n
                        iter_hour = 0
                        if iter_mins >= 60:
                            if iter_mins % 60 == 0:
                                hours_added += 1
                        iter_mins = iter_mins % 60
                        iter_hour = hours_added
                        if iter_mins < 10:
                            iter_mins = '0' + str(iter_mins)
                        else:
                            iter_mins = str(iter_mins)
                        if iter_hour < 10:
                            iter_hour = '0' + str(iter_hour)
                        else:
                            iter_hour = str(iter_hour)
                        to_cvs_hour = iter_hour + ':' + iter_mins
                        writer = csv.writer(f)
                        writer.writerow([to_cvs_hour, "Sin datos: Script offline"])
        else:
            pass



def func():
    csvfile = 'data/' + 'UberX ' + datetime.now().strftime("%d %m %Y") + '.csv'
    if os.path.exists(csvfile) == False:
        with open(csvfile, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Hora", "Precio"])
    offline_row_filler()
    hora = datetime.now().strftime("%H:%M")
    response = requests.request("POST", url, headers=headers, data=payload)
    fare = json.loads(response.text)['data']['products']['tiers'][0]['products'][0]['fare'][4:]
    data = [hora, fare]
    with open(csvfile, 'a', newline='') as file:
        writer = csv.writer(file)
        try:
            writer.writerow(data)
            print(data)
        except:
            print('Error: ' + f'{response.text}')
            error = [hora, 'Sin datos: Error']
            writer.writerow(error)

schedule.every(config.interval).minutes.at(":00").do(func)
while True:
    schedule.run_pending()
    time.sleep(1)