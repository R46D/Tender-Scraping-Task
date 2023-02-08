#Required libraries to download if not already installed
'''!pip3 install pandas
   !pip3 install selenium
   !pip3 install webdriver_manager
  '''

#Importing Required libraries

import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

#running the driver
driver = webdriver.Chrome(ChromeDriverManager().install())

#opening the website

driver.get('https://etenders.gov.in/eprocure/app?page=FrontEndTendersByOrganisation&service=page')

#scraping the main table from website

webtable_df = pd.read_html(driver.find_element(By.XPATH,'//*[@id="table"]').get_attribute('outerHTML'))[0]

#making First row as headers

webtable_df.columns=webtable_df.iloc[0]
webtable_df=webtable_df[1:]

#removing null values

webtable_df.dropna(inplace=True)

#converting tender count column as integer

webtable_df['Tender Count'] = webtable_df['Tender Count'].astype('int')

#finding sub-links from tender count column

links=driver.find_elements(By.CLASS_NAME,'link2')

#extracting the urls

urls=[]
for link in links:
    a=link.get_attribute('href')
    urls.append(a)
    
#scraping the sub-tables from the urls
tlf=[]
table2=pd.DataFrame()
for i in range(len(urls)):
    driver.get(urls[i])
    webtable2_df = pd.read_html(driver.find_element(By.XPATH,'//*[@id="table"]').get_attribute('outerHTML'))[0]
    webtable2_df.columns=webtable2_df.iloc[0]
    webtable2_df=webtable2_df[1:]

    #Getting the links to tender information    
    
    tls=driver.find_elements(By.XPATH,'//*[@title="View Tender Information"]')
    for tl in tls:
        b=tl.get_attribute('href')
        tlf.append(b)
    table2=table2.append(webtable2_df)
    

    
#removing null values
table2.dropna(inplace=True)

#adding tender links to table

table2['Tender Links']=tlf

#closing the browser

driver.quit()

#adding the organisation name to scraped table
on=[]
for i in range(1,len(webtable_df['S.No'])+1):
    for j in range(1,webtable_df['Tender Count'][i]+1):
        on.append(webtable_df['Organisation Name'][i])
        
table2['Organisation Name']=on

#Reseting the Serial No. of the table
Sno=[]
for i in range(1,len(table2['S.No'])+1):
    Sno.append(i)
    
table2['S.No']=Sno

#Converting the column data types to the correct one

table2['S.No'] = table2['S.No'].astype('int')

table2[['e-Published Date','Closing Date','Opening Date']] = table2[['e-Published Date','Closing Date','Opening Date']].apply(pd.to_datetime)

#Exporting the final table

table2.to_csv('Tenders_Final.csv',index=False)

