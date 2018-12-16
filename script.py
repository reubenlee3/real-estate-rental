import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
%matplotlib inline

#this is for determining the postal district
#define two search parameters
district = []
bedroom = []

#upload data file for list of postal areas
postal_areas = pd.read_csv("/Users/smu/Desktop/Data Science stuff/rental units project/list-of-postal-districts.csv")

preferred_area = "ang mo kio"
preferred_area = preferred_area.title()

#bedroom number parameter
bedroom = 3

#for i in range(0,len(postal_areas.index)):
district_code = postal_areas[postal_areas["General Location"].str.contains(preferred_area)]
postal_district = int(district_code['Postal District'])

if (postal_district == 0):
    print("Your Area is sadly not in our repository")

#web scraper
from bs4 import BeautifulSoup
import urllib.request
import csv
import requests
import folium
from geopy.geocoders import Nominatim
import random
import time

address = []
pp = []

for j in range(1,5):
    
    #extract webpage html, including multiple pages of the webpage
    url1 = 'https://www.iproperty.com.sg/rent/district-' + str(postal_district)+ '/hdb/?bedroom=' + str(bedroom) + '&page=' + str(j)
    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    page = requests.get(url1,headers= headers)#urllib.request.urlopen(url1)
    soupysoupy = BeautifulSoup(page.text,'html.parser')

    geolocator = Nominatim(user_agent = "Jalaba")
    
    #create address list
    addr = soupysoupy.find_all("div",{'class':'fsKEtj'})
    
    for a in addr:
        data_addr = a.text.strip()
        address.append(data_addr)


    #create price list
    price = soupysoupy.find_all("div",{'class':'hzTrLN'})
    
    for p in price:
        data_price = p.text.strip()
        pp.append(data_price)
    
    #create sqft list 
    sqft = soupysoupy.find_all('a',{'class':'attrs-price-per-unit-desktop'})
    
    for a in sqft:
        data_sqft = a.text.strip()
        squarefeet.append(data_sqft)
    
    #function to not scrap the website too aggressively
    time.sleep(random.randint(1,10))

address_df = pd.DataFrame(address,columns=['Address'])
price_df = pd.DataFrame(pp,columns=['Price'])
sqft_df = pd.DataFrame(squarefeet,columns=['Square Feet'])

#combine both dataframes and clean the data a bit
full_data = pd.concat([address_df,price_df,sqft_df],axis=1)

full_data = full_data.replace({'SGD':''},regex=True)
full_data = full_data.replace({',':''},regex = True)
full_data = full_data.replace({'Blk':''},regex = True)
full_data = full_data.replace({'Built-up : ':''},regex = True)

for k in range(0,len(full_data.index)):
    if (full_data['Square Feet'][k][-6:] == 'sq. m.'):
        full_data['Square Feet'][k] = full_data['Square Feet'][k].replace(' sq. m.','')
        full_data['Square Feet'][k] = int(full_data['Square Feet'][k]) * 10.764

full_data = full_data.replace({' sq. ft.':''},regex = True)
full_data["Address"] = full_data['Address'].str.slice(0,-7,1)
full_data['Price'] = pd.to_numeric(full_data['Price'])
full_data['Square Feet'] = pd.to_numeric(full_data['Square Feet'])


#now lets filter out the weird stuff eg rooms that are not accurately labelled
full_data_clean = full_data[full_data['Square Feet'] > 150 * int(bedroom)]
full_data_clean


#create empty lists to store values later on
location = []
lat = []
long = []
    
#create empty lists to store values later on
location = []
lat = []
long = []
    
#loop through the addresses collected from the website to generate latitude and longitude values
for i in range(0,len(full_data.index)):
    locator = geolocator.geocode(str(full_data['Address'][i]))
    location.append(locator)
    lat.append(location[i][1][0])
    long.append(location[i][1][1])

#create the latitude and longitude dataframes
lat_df = pd.DataFrame(lat,columns=["Latitude"])
long_df = pd.DataFrame(long,columns=["Longitude"])

#combine the lat and long df into the main dataset
full_data_clean = pd.concat([full_data_clean,lat_df,long_df],axis = 1)

#create a map of singapore
location = [1.3521,103.8198]
sgmap = folium.Map(location,zoom_start = 12)


#store latitude data and longitude data in dataframes
latitude = full_data_clean["Latitude"]
longitude = full_data_clean['Longitude']
price = full_data_clean['Price']

#create a colour coding function
lower_price_bracket = np.percentile(full_data_clean['Price'],30)
mid_price_bracket = np.percentile(full_data_clean['Price'],70)

def colourcode(price):
    if (price < lower_price_bracket):
        return('green')
    elif (price >= lower_price_bracket and price < mid_price_bracket):
        return('orange')
    else:
        return('red')

#loop to find the houses on the map using coordinates
for latitude,longitude,price in zip(latitude,longitude,price):
    folium.Marker(location = [latitude,longitude], icon = folium.Icon(color = colourcode(price))).add_to(sgmap)

sgmap
