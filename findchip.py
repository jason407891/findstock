import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime


pn="39-00-0038"
url = "https://www.findchips.com/search/"+str(pn)
response = requests.get(url)


def findchips(response,supplier_code,name, profit):
    price_results=[]
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        try:
            rows = soup.find(id="list"+str(supplier_code)).find_all(class_="row")
            for row in rows:
                price_result={}
                price_result["supplier_code"]=supplier_code
                #pn
                pn =row.find(class_="onclick")
                pn=pn.text.strip()
                if pn!=name:
                    break
                price_result["pn"]=pn
                #mfr
                mfr=row.find(class_="td-mfg")
                mfr=mfr.text.strip()
                price_result["mfr"]=mfr
                #stock
                stock=row.find(class_="td-stock")
                stock=stock.text.strip()
                match = re.search(r'\d+\.\d+|\d+', stock)
                if match:
                    found_number = match.group()
                    if int(found_number)==0:
                        break
                    price_result["stock"]=stock
                #price_break
                prices=row.find_all(class_="price-list")
                price_breaks=[] # []
                for price in prices:
                    labels = price.find_all(class_="label")
                    values = price.find_all(class_="value")
                    for i in range(len(labels)):
                        base_price=values[i]['data-baseprice'].strip()
                        resultprice=round(float(base_price)*profit,2)
                        price_info = {
                            "goods_num":labels[i].text.strip(),
                            "goods_price":resultprice
                        }
                        price_breaks.append(price_info)
                price_result["price"] = price_breaks
                current_time=datetime.now()
                date=current_time.date()
                datestr= date.strftime("%Y-%m-%d")
                price_result["date"] = datestr
                price_results.append(price_result)                  
            return(price_results)
        except:
            return([])
    else:
        return({"results":"SOMETHING ERROR"})

def findchipsDes(response,supplier_code,name, profit):
    price_results=[]
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        try:
            rows = soup.find(id="list"+str(supplier_code)).find_all(class_="row")
            for row in rows:
                price_result={}
                price_result["supplier_code"]=supplier_code
                #pn
                pn =row.find(class_="onclick")
                pn=pn.text.strip()
                if pn!=name:
                    break
                price_result["pn"]=pn
                #mfr
                mfr=row.find(class_="td-mfg")
                mfr=mfr.text.strip()
                price_result["mfr"]=mfr
                #stock
                stock=row.find(class_="td-stock")
                stock=stock.text.strip()
                match = re.search(r'\d+\.\d+|\d+', stock)
                if match:
                    found_number = match.group()
                    if int(found_number)==0:
                        break
                    price_result["stock"]=stock
                #price_break
                prices=row.find_all(class_="price-list")
                price_breaks=[] # []
                for price in prices:
                    labels = price.find_all(class_="label")
                    values = price.find_all(class_="value")
                    for i in reversed(range(len(labels))):
                        base_price=values[i]['data-baseprice'].strip()
                        resultprice=round(float(base_price)*profit,2)
                        price_info = {
                            "goods_num":labels[i].text.strip(),
                            "goods_price": resultprice
                        }
                        price_breaks.append(price_info)
                price_result["price"] = price_breaks
                current_time=datetime.now()
                date=current_time.date()
                datestr= date.strftime("%Y-%m-%d")
                price_result["date"] = datestr
                price_results.append(price_result)                  
            return(price_results)
        except:
            return([])
    else:
        return({"results":"SOMETHING ERROR"})




def findchips_qty(response,supplier_code,name,qty):
    price_results=[]
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        try:
            rows = soup.find(id="list"+str(supplier_code)).find_all(class_="row")
            for row in rows:
                price_result={}
                price_result["supplier_code"]=supplier_code
                #pn
                pn =row.find(class_="onclick")
                pn=pn.text.strip()
                if pn!=name:
                    break
                price_result["pn"]=pn
                #mfr
                mfr=row.find(class_="td-mfg")
                mfr=mfr.text.strip()
                price_result["mfr"]=mfr
                #stock
                stock=row.find(class_="td-stock")
                stock=stock.text.strip()
                match = re.search(r'\d+\.\d+|\d+', stock)
                if match:
                    found_number = match.group()
                    if int(found_number)==0:
                        break
                    price_result["stock"]=int(found_number)
                #price_break
                prices=row.find_all(class_="price-list")
                price_breaks=[] # []
                price_breaks.append("")
                for price in prices:
                    labels = price.find_all(class_="label")
                    values = price.find_all(class_="value")
                    price_info = {
                            "goods_num":labels[0].text.strip(),
                            "goods_price":values[0].text.strip()
                        }
                    price_breaks[0]=price_info
                    
                    for i in range(1,len(labels)):
                        if qty<int(labels[i].text.strip()):
                            break
                        price_info = {
                            "goods_num":labels[i].text.strip(),
                            "goods_price":values[i].text.strip()
                        }
                        price_breaks[0]=price_info


                price_result["price"] = price_breaks
                price_results.append(price_result)                  
            return(price_results)
        except:
            return([])
    else:
        return({"results":"SOMETHING ERROR"})


def findchips_desqty(response,supplier_code,name,qty):
    price_results=[]
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        try:
            rows = soup.find(id="list"+str(supplier_code)).find_all(class_="row")
            for row in rows:
                price_result={}
                #price_result["supplier_code"]=supplier_code
                #pn
                pn =row.find(class_="onclick")
                pn=pn.text.strip()
                if pn!=name:
                    break
                price_result["pn"]=pn
                #mfr
                mfr=row.find(class_="td-mfg")
                mfr=mfr.text.strip()
                price_result["mfr"]=mfr
                #stock
                stock=row.find(class_="td-stock")
                stock=stock.text.strip()
                match = re.search(r'\d+\.\d+|\d+', stock)
                if match:
                    found_number = match.group()
                    if int(found_number)==0:
                        break
                    price_result["stock"]=int(found_number)
                #price_break
                prices=row.find_all(class_="price-list")
                price_breaks=[] # []
                price_breaks.append("")
                for price in prices:
                    labels = price.find_all(class_="label")
                    values = price.find_all(class_="value")
                    price_info = {
                            "goods_num":labels[0].text.strip(),
                            "goods_price":values[0].text.strip()
                        }
                    price_breaks[0]=price_info
                    
                    for i in range(len(labels)-1,-1,-1):
                        if qty<int(labels[i].text.strip()):
                            break
                        price_info = {
                            "goods_num":labels[i].text.strip(),
                            "goods_price":values[i].text.strip()
                        }
                        price_breaks[0]=price_info
                price_result["price"] = price_breaks
                price_results.append(price_result)                  
            return(price_results)
        except:
            return([])
    else:
        return({"results":"SOMETHING ERROR"})
    


"""
DGKEY 1588
CHIPONE 4327862
AVNET 313766970
ELEMENT 2953375
MOUSER 1577
TME 150002559
TTI 1545
"""


#print(findchips(response,1588,pn))
#a=findchips_qty(response,1545,pn,900)
#print(findchips(response,1588,pn))