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
    pool_size=5,  # 适当调整池的大小
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

@app.route("/api/product/<partnumber>",methods=["POST","GET","DELETE"])
def handle_search(partnumber):
	db=client['pteam']
	collection=db['linestock']
	if request.method == "GET":
		try:
			query={"pn":partnumber}
			results = collection.find(query)
			data=list(results)
			# 將所有的 NaN 值轉換成 "NA"
			for item in data:
				for key, value in item.items():
					if isinstance(value, float) and math.isnan(value):
						item[key] = "NA"
			for item in data:
				item['_id'] = str(item['_id'])
			return jsonify({"data":data})
		except Exception as e:
			return jsonify({"data":e})
	elif request.method == "POST":
		data=request.get_json()
		data["pn"] = partnumber
		current_time=datetime.now()
		date=current_time.date()
		datestr= date.strftime("%Y-%m-%d")
		data["date"] = datestr
		data["price"] = '[{"goods_price": "請洽業務", "goods_num": "1"}]'
		result = collection.insert_one(data)
		return jsonify({"message": "Product added successfully", "id": str(result.inserted_id)})
	elif request.method== "DELETE":
		data=request.get_json()
		filter_field={
			"date":data["date"],
			"pn":partnumber
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
		df = pd.read_excel(upload_file)
		data = df.to_dict(orient="records")
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
		print(data)
		
		result = collection.insert_many(data)
		return jsonify({"message": "Product added successfully"})
	except Exception as e:
		return jsonify({"message":str(e)})


@app.route("/api/showstock",methods=["POST"])
def api_showstock():
	db=client['pteam']
	collection=db['linestock']
	data=request.get_json()
	supplier=data["supplier"]
	query={"supplier":supplier}
	data=list(collection.find(query).limit(10))
	new_data=[]
	for item in data:
		item["_id"]=str(item["_id"])
		new_data.append(item)
	print(new_data)

	return jsonify({"data": new_data})


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


app.run(host="0.0.0.0", port=3000)