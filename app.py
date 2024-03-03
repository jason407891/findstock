from flask import *
import mysql.connector
from datetime import datetime
import mysql.connector
from mysql.connector import pooling
import requests
import boto3
from botocore.exceptions import NoCredentialsError
import os
import pymongo
import requests
import math
import pandas as pd
import jwt
from jwt.exceptions import DecodeError
import findchip
import mouser
import json
from operator import itemgetter

aws_access_key_id = "AKIAUFTPQN5O75N6A7EW"
aws_secret_access_key = "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"


client = pymongo.MongoClient("mongodb+srv://root:12root28@cluster0.r39qy0s.mongodb.net/?retryWrites=true&w=majority")

app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False
app.config["JSONIFY_MIMETYPE"] = 'application/json; charset=utf-8'
app.config ['JSON_SORT_KEYS'] = False
secret_key = "jasonkey"

dbconfig = {
    "host": "mydbinstance.coduydqlqucg.us-east-1.rds.amazonaws.com",
    "user": "myuser",
    "password": "mypassword",
    "database": "mydatabase",
    "port": 3306,
}

connection_pool = pooling.MySQLConnectionPool(
    pool_name="my_pool",
    pool_size=5, 
    **dbconfig
)


@app.route("/")
def index():
	return render_template("index.html")

@app.route("/product/<pn>")
def product(pn):
	return render_template("list.html")

@app.route("/stock")
def stock():
	return render_template("stock.html")

@app.route("/bom")
def bom():
	return render_template("bom.html")

@app.route("/contact")
def contact():
	return render_template("contact.html")

@app.route("/rfq")
def rfq():
	return render_template("rfq.html")


@app.route("/admin")
def admin():
	return render_template("admin.html")


@app.route("/api/agent/product/<partnumber>",methods=["GET","POST"])
def handle_agent(partnumber):
	try:
		url = "https://www.findchips.com/search/"+str(partnumber)
		response = requests.get(url)
		result_dg=findchip.findchipsDes(response,1588,partnumber,32*1.1) # DGKEY
		result_mouser=findchip.findchips(response,1577,partnumber,32*1.1) # MOUSER
		result_tti=findchip.findchips(response,1545,partnumber,32*1.3) # TTI
		result_element=findchip.findchipsDes(response,2953375,partnumber,1.1) # ELEMENT
		result_arrow=findchip.findchipsDes(response,1538,partnumber,32*1.2) #ARROW
		result_master=findchip.findchipsDes(response,1560,partnumber,32*1.3) #MASTER
		return jsonify({"data":[result_dg,result_mouser,result_tti,result_element,result_arrow,result_master]})
	except Exception as e:
		return jsonify({"data":e})




@app.route("/api/product/<partnumber>",methods=["POST","GET","DELETE"])
def handle_search(partnumber):
	db=client['pteam']
	collection=db['linestock']
	if request.method == "GET":
		try:
			query = {"pn": partnumber}
			results = collection.find(query)	
			data=list(results)
			# 將所有的 NaN 值轉換成 "NA"
			for item in data:
				for key, value in item.items():
					if isinstance(value, float) and math.isnan(value):
						item[key] = "NA"
			for item in data:
				item['_id'] = str(item['_id'])
			return_data=[]
			for item in data:
				#將price變陣列
				price_str = item.get("price","NA")
				price_data = json.loads(item.get("price", "[]"))
				partial = {
					"date":item.get("date","NA"),
					"pn": item.get("pn","NA"),
					"mfr": item.get("mfr","NA"),
					"qty": item.get("qty","NA"),
					"price": price_data,
					"dc": item.get("dc","NA"),
					"location": item.get("location","NA"),
					"coo": item.get("coo","NA"),
					"noted": item.get("noted","NA")
				}
				return_data.append(partial)
			return jsonify({"data":return_data})
		except Exception as e:
			return jsonify({"data":e})
	elif request.method == "POST":
		try:
			data = request.form.to_dict()
			data["pn"] = partnumber
			current_time=datetime.now()
			date=current_time.date()
			datestr= date.strftime("%Y-%m-%d")
			data["date"] = datestr
			data["price"] = '[{"goods_price": "請洽業務", "goods_num": "1"}]'
			result = collection.insert_one(data)
			#處理上傳圖片
			if 'profile' in request.files and request.files['profile']:
				file = request.files['profile']
				s3 = boto3.client('s3',region_name='ap-southeast-2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
				timestring=str(datetime.now().minute)+str(datetime.now().second)
				filename=data["pn"]+"_"+timestring+".png"
				s3.upload_fileobj(file,"findstock",filename)
				s3.put_object_acl(Bucket='findstock', Key=filename, ACL='public-read') #設定成公開
			return jsonify({"message": "Product added successfully", "id": str(result.inserted_id)})
		except Exception as e:
			return jsonify({"message":str(e)}),500
	elif request.method== "DELETE":
		data=request.get_json()
		#有料號的情況
		if "pn" in data:
			filter_field={
				"date": data["date"],
				"pn": data["pn"],
				"supplier": data["supplier"]
			}
			print(data["date"])
		#刪除同日期上傳的所有料號
		else:
			filter_field={
				"date": data["date"],
				"supplier": data["supplier"]
			}
		result = collection.delete_many(filter_field)
		if result.deleted_count == 0:
			return jsonify({"message": "Product not deleted successfully"})
		else:
			return jsonify({"message": "deleted successfully"})

@app.route("/api/products",methods=["POST"])
def api_products():
	db=client['pteam']
	collection=db['linestock']
	try:
		upload_file = request.files["file"]
		supplier = request.form.get("supplier")
		df = pd.read_excel(upload_file, dtype={"pn": str})
		df.fillna('NA', inplace=True)
		data = df.to_dict(orient="records")
		insert_data = []
		for insert_stock in data:
			insert_stock["supplier"] = supplier
			current_time = datetime.now()
			datestr = current_time.strftime("%Y-%m-%d")
			insert_stock["date"] = datestr
			if "price" not in insert_stock:
			    insert_stock["price"] = '[{"goods_price": "請洽業務", "goods_num": "1"}]'
			insert_data.append(insert_stock)
		if insert_data:
			collection.insert_many(insert_data)
			return jsonify({"message": "Products added successfully"})
		'''
		for insert_stock in data:
			#處理excel表格裡面的supplier欄位
			insert_stock["supplier"]=supplier
			current_time=datetime.now()
			date=current_time.date()
			datestr= date.strftime("%Y-%m-%d")
			#處理excel表格裡面的date欄位
			insert_stock["date"] = datestr
			#處理excel表格裡面的price欄位
			if "price" not in insert_stock:
				insert_stock["price"] = '[{"goods_price": "請洽業務", "goods_num": "1"}]'
			existing_record = collection.find_one({"pn": insert_stock["pn"], "supplier": supplier})
			if existing_record:
	  			collection.update_one({"_id": existing_record["_id"]}, {"$set": insert_stock})
			else:
				collection.insert_one(insert_stock)
		return jsonify({"message": "Product added successfully"})
		'''
	except Exception as e:
		return jsonify({"message":str(e)})


@app.route("/api/showstock",methods=["POST"])
def api_showstock():
	db=client['pteam']
	collection=db['linestock']
	data=request.get_json()
	supplier=data["supplier"]
	page = int(data.get("page", 1))  # 默認為第1頁
	page_size = int(data.get("page_size", 10))  # 默認每頁10條記錄

	offset = (page - 1) * page_size

	query = {"supplier": supplier}
	total_items = collection.count_documents(query)
	data = list(collection.find(query).sort("_id", -1).skip(offset).limit(page_size))
	#data=list(collection.find(query).sort("_id",-1).limit(50))
	new_data=[]
	for item in data:
		item["_id"]=str(item["_id"])
		new_data.append(item)

	return jsonify({
		"data": new_data,
        "total_items": total_items,
        "page": page,
        "page_size": page_size,
        "total_pages": (total_items + page_size - 1) // page_size
		})

@app.route("/api/adminGetUser", methods=["GET"])
def admin_user():
	connection = connection_pool.get_connection()
	try:
		cursor = connection.cursor(dictionary=True)
		cursor.execute("SELECT * FROM users")
		users = cursor.fetchall()
		cursor.close()
		return jsonify(users), 200
	except Exception as e:
		return jsonify({"error": True, "message": str(e)}), 500
	finally:
		connection.close()


@app.route("/api/info/product/<partnumber>",methods=["GET","POST"])
def api_productinfor(partnumber):
	try:
		response=mouser.getdata(partnumber)
		return jsonify({"data":response})
	except Exception as e:
		return jsonify({"data":e})



@app.route("/api/user", methods=["GET","POST"])
def api_user():
	connection = connection_pool.get_connection()
	try:
		data = request.get_json()
		name = data.get('name')
		email = data.get('email')
		password = data.get('password')
		phone = data.get('phone')
		company_name = data.get('company_name')
		tax_id = data.get('tax_id')
		address = data.get('address')
		brand = data.get('brand')

		try:
			cursor = connection.cursor()
			cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
			existing_user = cursor.fetchone()
			cursor.close()
			if existing_user:
				return jsonify({"error":True, "message":"Email already exist"}), 400
			
			cursor = connection.cursor()
			cursor.execute("INSERT INTO users (name, email, password, company_name, tax_id, address, brand, phone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (name, email, password, company_name, tax_id, address, brand, phone))
			connection.commit()
			cursor.close()

			return jsonify({"ok": True}), 200
		except Exception as e:
			return jsonify({"error":True,"message":str(e)}), 500
	finally:
	    connection.close()


@app.route("/api/user/auth", methods=["PUT","GET"])
def api_login():
    connection = connection_pool.get_connection()
    try:
        if request.method == "PUT":
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            cursor = connection.cursor()
            cursor.execute("SELECT user_id, name, email, company_name FROM users WHERE email = %s AND password = %s", (email, password))
            user = cursor.fetchone()
            cursor.close()

            if user:
                user_info = {
                    "user_id": user[0],
                    "name": user[1],
                    "email": user[2],
                }
                # 生成 JWT Token
                token = jwt.encode(user_info, secret_key, algorithm="HS256")

                return jsonify({"token": token,"company_name":user[3]})
            else:
                return jsonify({"error":True, "message":"帳號或是密碼輸入錯誤"}), 400
        elif request.method == "GET":
            token = request.headers.get("Authorization")
            if token=="null":
                return jsonify({"error":True,"message":"user not login"}), 200
            try:
                user_info = jwt.decode(token, secret_key, algorithms=["HS256"])
                return jsonify({"data": user_info})
            except DecodeError as e:
                return jsonify({"error":True,"message":str(e)}), 500
    finally:
        connection.close()


@app.route("/api/rfq/",methods=["GET","POST","DELETE"])
def api_rfq():
	connection = connection_pool.get_connection()
	try:
		if request.method == "GET":
			try:
				company_name=request.args.get("companyname")
				cursor = connection.cursor()
				query = "SELECT * FROM rfqlist WHERE company_name = %s"
				cursor.execute(query, (company_name,))
				results = cursor.fetchall()
				rfqlists = []
				item_count=1
				for row in results:
					rfqlist = {
						"rfq_id":row[0],
						"itemcount":item_count,
						"customer_name": row[1],
						"mfr":row[2],
						"pn":row[3],
						"qty":row[4],
						"suggest_price":row[5],
						"remarks":row[6],
						"time":row[7]
					}
					rfqlists.append(rfqlist)
					item_count+=1
				return jsonify({"response":rfqlists})
			except Exception as e:
				return jsonify({"error":True, "response":str(e)}),500
		elif request.method=="POST":
			try:
				data=request.get_json()
				company_name=data["company_name"]
				mfr=data["mfr"]
				pn=data["pn"]
				qty=data["qty"]
				price=data.get("price","NA")
				remarks=data.get("remarks","NA")
				cursor = connection.cursor()
				query = "INSERT INTO rfqlist (company_name, mfr, pn, qty, suggested_price, remarks) VALUES (%s, %s, %s, %s, %s, %s)"
				cursor.execute(query, (company_name, mfr, pn, qty, price, remarks))
				connection.commit()
				return jsonify({"message":"create successfully"})
			except Exception as e:
				return jsonify({"error":True, "response":str(e)}),500
		elif request.method=="DELETE":
			try:
				company_name=request.args.get("companyname")
				cursor = connection.cursor()
				query = "DELETE FROM rfqlist WHERE company_name = %s"
				cursor.execute(query,(company_name,))
				connection.commit()
				return jsonify({"message": "ALL Record deleted successfully"})
			except Exception as	e:
				return jsonify({"error": True, "response": str(e)}), 500
	finally:
		connection.close()


@app.route("/api/rfq/<int:data_id>",methods=["DELETE"])
def delete_rfq(data_id):
	connection = connection_pool.get_connection()
	try:
		cursor = connection.cursor()
		query = "DELETE FROM rfqlist WHERE id = %s"
		cursor.execute(query,(data_id,))
		connection.commit()
		return jsonify({"message": "Record deleted successfully"})
	except Exception as	e:
	    return jsonify({"error": True, "response": str(e)}), 500
	finally:
		connection.close()


def format_cell(content, width=12):
    return (content + ' ' * width)[:width]

@app.route("/api/rfqtoDC",methods=["POST"])
def api_rfqtodc():
    webhook_url="https://discord.com/api/webhooks/1163495849842704565/I7SJdtkonFMMvuXFs3GQTshXtwCB47N3juFGLNtBf1bLAevRIXukZdH82j31jfhRbCxQ"
    data=request.get_json()
    table = "```\n"
    table += "RFQ客戶:"+data["companyname"]+"\n"
    table += "| " + format_cell("項次",width=2) + "| " + format_cell("製造商",width=6)
    table += "| " + format_cell("產品編號",width=8) + "| " + format_cell("需求數量",width=4)
    table += "| " + format_cell("建議價格",width=8) + "|\n"
    for item in data['content']:
        table += "| " + format_cell(item['itemid'],width=4)
        table += "| " + format_cell(item['mfr'],width=8)
        table += "| " + format_cell(item['pn'])
        table += "| " + format_cell(item['qty'],width=6)
        table += "| " + format_cell(item['price']) + "|\n"
    table += "```"

    discord_data = {"content": table}
    headers = {'Content-Type': 'application/json'}
    requests.post(webhook_url, data=json.dumps(discord_data), headers=headers)
    return jsonify({"message": "RFQ send successfully"})

@app.route("/api/feedbacktoDC",methods=["POST"])
def api_feedbacktoDC():
	try:
		webhook_url="https://discord.com/api/webhooks/1163495849842704565/I7SJdtkonFMMvuXFs3GQTshXtwCB47N3juFGLNtBf1bLAevRIXukZdH82j31jfhRbCxQ"
		data=request.get_json()
		content="客戶名稱: "+data["companyname"]+"\n"
		content+="建議內容: "+data["content"]
		output={"content":content}
		headers = {'Content-Type': 'application/json'}
		requests.post(webhook_url, data=json.dumps(output), headers=headers)
		return jsonify({"message": "feedback send successfully"})
	except Exception as e:
		return jsonify({"message": "fail to give feedback"+str(e)})

@app.route("/api/image/product/<partnumber>")
def api_showUploadImage(partnumber):
	try:
		s3 = boto3.client('s3',region_name='ap-southeast-2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
		response = s3.list_objects_v2(Bucket="findstock", Prefix=partnumber)

		files = []
		if 'Contents' in response:
			for item in response['Contents']:
				files.append(item['Key'])

		return jsonify({"data":files})
	except Exception as e:
		return jsonify({"data":str(e)}),500

@app.route("/api/allimg")
def api_allimg():
	try:
		s3 = boto3.client('s3',region_name='ap-southeast-2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
		response = s3.list_objects_v2(Bucket="findstock")
		files = []
		if 'Contents' in response:
			sorted_files = sorted(response['Contents'], key=itemgetter('LastModified'), reverse=True)
			for item in sorted_files[:20]:
				files.append(item['Key'])
		return jsonify({"data":files})
	except Exception as e:
		return jsonify({"data":str(e)}),500

@app.route("/api/getAllBrand")
def api_allbrand():
	db=client['pteam']
	collection=db['linestock']
	distinct_brands = collection.distinct('mfr')
	return jsonify({"data":distinct_brands})



app.run(host="0.0.0.0", port=3000)