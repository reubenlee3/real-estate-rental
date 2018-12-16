import pandas as pd
import numpy as np
import matplotlib as plt
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

    addr = soupysoupy.find_all("div",{'class':'fsKEtj'})
    
    for a in addr:
        data_addr = a.text.strip()
        address.append(data_addr)


    #create price dataframe
    price = soupysoupy.find_all("div",{'class':'hzTrLN'})
    
    for p in price:
        data_price = p.text.strip()
        pp.append(data_price)
    
    time.sleep(random.randint(1,10))

address_df = pd.DataFrame(address,columns=['Address'])
price_df = pd.DataFrame(pp,columns=['Price'])

#combine both dataframes and clean the data a bit
full_data = pd.concat([address_df,price_df],axis=1)
full_data = full_data.replace({'SGD':''},regex=True)
full_data = full_data.replace({',':''},regex = True)
full_data = full_data.replace({'Blk':''},regex = True)
full_data["Address"] = full_data['Address'].str.slice(0,-7,1)
full_data['Price']=pd.to_numeric(full_data['Price'])

location = []
lat = []
long = []
    
for i in range(0,len(full_data.index)):
    locator = geolocator.geocode(str(full_data['Address'][i]))
    location.append(locator)
    lat.append(location[i][1][0])
    long.append(location[i][1][1])

lat_df = pd.DataFrame(lat,columns=["Latitude"])
long_df = pd.DataFrame(long,columns=["Longitude"])

full_data = pd.concat([full_data,lat_df,long_df],axis = 1)

location = [1.3700,103.8496]
sgmap = folium.Map(location,zoom_start = 15)

#plot the marker for the area in question
folium.Marker(location = [1.3700,103.8496], icon = folium.Icon(color = 'red')).add_to(sgmap)

#store latitude data and longitude data in dataframes
latitude = full_data["Latitude"]
longitude = full_data['Longitude']
price = full_data['Price']

#create a colour coding function
lower_price_bracket = np.percentile(full_data['Price'],30)
mid_price_bracket = np.percentile(full_data['Price'],70)

def colourcode(price):
    if (price < lower_price_bracket):
        return('black')
    elif (price >= lower_price_bracket and price < mid_price_bracket):
        return('green')
    else:
        return('red')

#loop to find the houses on the map using coordinates
for latitude,longitude,price in zip(latitude,longitude,price):
    folium.Marker(location = [latitude,longitude], icon = folium.Icon(color = colourcode(price))).add_to(sgmap)

sgmap
