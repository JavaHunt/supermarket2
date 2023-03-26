from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse
import dbconnect
import global_data as gd
from translate import *
from json import dump
from datetime import datetime

# Create your views here.
cursor = dbconnect.conn.cursor(buffered=True, dictionary=True)
import os
Filepath = os.path.join(os.getenv('USERPROFILE'),'Downloads')
Filepath = Filepath + "\sample.txt"

obj = datetime.now()
date = obj.strftime("%Y-%m-%d")
time = obj.strftime("%X")

# list of scanned items for billing
scanned_products = []
incIndex = 1

def home(request):
    
    if gd.uname == '' and gd.passw == '':
        return redirect('/login/')
    return render(request, 'index.html')

def login(request):

    gd.uname = ''
    gd.passw = ''
    gd.phno = ''
    gd.role = ''
    #Executing an MYSQL function using the execute() method
    cursor.execute("SELECT * from users")

    # Fetch all rows using fetchall() method.
    data = cursor.fetchall()
    if request.method == "POST":
        gd.uname = request.POST['username']
        gd.passw = request.POST['password']
        for i in data:
            if i['username'] == gd.uname and i['password'] == gd.passw:
                if i['status'] == 1:
                    return HttpResponse("<h1> Same user in mutliple devices are not allowed </h1>")
                else:
                    # query = f"update users set status = 1 where username = '{i['username']}'"
                    # cursor.execute(query)
                    if i['role'] == 'accountant':
                        gd.role = 'accountant'
                        return redirect('/accountant/')
                    elif i['role'] == 'admin':
                        gd.role = 'admin'
                        return redirect('/smadmin/')
                    else:
                        return HttpResponse("<h4>User not defined</h4>")
        else:
            return HttpResponse("<h1>Login not successful</h1>")
    else:
        return render(request, 'login.html', {})


def accountant(request):
    if gd.uname == '':
        return redirect('/login/')
    else:
        global scanned_products
        scanned_products = []
        from datetime import timedelta, date
        today = date.today()
        yesterday = today - timedelta(days = 1)
        query = f"select product_no as id, product_name as name, sum(qnty) as qnty, sum(price) as price, sum(save) as save, \
            sum(total) as total from transactions where bill_date = '{yesterday}' group by product_name"
        cursor.execute(query)
        translist = cursor.fetchall()
        context = {
            'trans':translist
        }
        return render(request, 'accountant.html', context)

def smadmin(request):
    if gd.uname == '':
        return redirect('/login/')
    else:
        from datetime import timedelta, date
        today = date.today()
        yesterday = today - timedelta(days = 1)
        week = today - timedelta(days=7)
        cursor.execute("SELECT * FROM pipeline order by token")
        pipeline_stocks = cursor.fetchall()

        # top 3 most frequent products purchased yesterday
        query = f"SELECT product_name, sum(qnty) as qnty from transactions where bill_date = '{yesterday}' \
            group by product_name order by sum(qnty) desc limit 3"
        cursor.execute(query)
        max_freq_stock = cursor.fetchall()

        # top 3 min frequent products purchased yesterday
        query = f"SELECT product_name, sum(qnty) as qnty from transactions where bill_date = '{yesterday}' \
            group by product_name order by sum(qnty) limit 3"
        cursor.execute(query)
        min_freq_stock = cursor.fetchall()

        # top 3 most frequent products purchased in week
        query = f"SELECT product_name, sum(qnty) as qnty from transactions where bill_date = '{yesterday}' \
            AND '{week}' group by product_name order by sum(qnty) desc limit 3"
        cursor.execute(query)
        max_week_freq_stock = cursor.fetchall()

        # top 3 min frequent products purchased in week
        query = f"SELECT product_name, sum(qnty) as qnty from transactions where bill_date = '{yesterday}' \
            AND '{week}' group by product_name order by sum(qnty) limit 3"
        cursor.execute(query)
        min_week_freq_stock = cursor.fetchall()
        context = {
            'pipeline_stocks' : pipeline_stocks,
            'max_freq_stocks' : max_freq_stock,
            'min_freq_stocks' : min_freq_stock,
            'max_week_freq_stocks' : max_week_freq_stock,
            'min_week_freq_stocks' : min_week_freq_stock,
        }
        if(request.method == 'POST'):
            x = request.POST["Bill_NO"]
            if x != '':
                gd.bill_no = x
            print('bill : ',request.POST.get("Bill_NO", 0))
            print("gd.bill : ", gd.bill_no)
            if request.POST["Bill_NO"] != '':
                
                query = f"SELECT * from transactions where bill_no = '{x}'"
                cursor.execute(query)
                res = cursor.fetchall()
                context["billNo"] = x
                context["transactions"] = res  # list of dictionaries

                # for Customer Number
                print(x)
                query = f"SELECT phno from transactions where bill_no = '{x}'"
                cursor.execute(query)
                res = cursor.fetchall()
                context["phno"] = res[0]['phno']
            
            # If Paid button clicked
            if request.POST["paid"] == "yes" and gd.bill_no != '':
                print(request.POST["type_of_trans"])
                mode = request.POST["type_of_trans"]
                if mode == '':
                    return HttpResponse("<h1>Enter Payment Mode</h1>")
                else:
                    query = f"UPDATE pipeline set paid='yes' where id='{gd.bill_no}'"
                    cursor.execute(query)

                    # check if bill_no already present or not
                    query = f"SELECT bill_no from payments where bill_no = '{gd.bill_no}'"
                    cursor.execute(query)
                    res = cursor.fetchall()
                    if(len(res) == 0):
                        query = f"INSERT INTO payments values('{gd.bill_no}', '{mode}')"
                        cursor.execute(query)
                    return redirect('/smadmin/')
                
            return render(request, 'admin.html', context)

        return render(request, 'admin.html', context)

def accountantStocksAvailable(request):
    global scanned_products
    scanned_products = []
    cursor.execute("SELECT * FROM stockavailable")
    stocks = cursor.fetchall()
    context = {
        'stocks_data': stocks
    }
    
    return render(request, 'stocks.html', context)

def adminStocksAvailable(request):
    cursor.execute("SELECT * FROM stockavailable")
    stocks = cursor.fetchall()
    context = {
        'stocks_data': stocks
    }
    
    return render(request, 'adminstocks.html', context)

def checkSID(sid):
    # Checking whether the product is available already in DB or not.
    # If available, just add the new stock count to it
    query = f"SELECT sid from stockavailable"
    cursor.execute(query)
    flag = False
    list_of_sids = cursor.fetchall()
    # flag is False, if no sid found
    for dict in list_of_sids:
        if dict['sid'] == str(sid):
            flag = True
            break
    print('flag = ', flag)
    return flag

def addStock(request):
    if request.method == "POST":
        print('post : ', request.POST)
        id = request.POST['sid'].lower()
        name = request.POST['name'].lower()
        netwt = request.POST['netwt'].lower()
        count = request.POST['count'].lower()
        price = request.POST['price'].lower()
        category = request.POST['category'].lower()
        #filen = request.FILES['filename']
        #print(filen)
        #for i in filen:
            #print(i)
        
        if id != '':
            try:
                count = int(count)
            except ValueError:
                return HttpResponse("<h3>Enter stock details correctly")
    
            
            if checkSID(id) == False:
                query = f"insert into stockavailable values('{id}', '{name}', {netwt}, '{category}', {count}, {price})"
                cursor.execute(query)
                return redirect('/addstock/')
            else:
                # Already product is available in DB
                tempQ = f"SELECT count from stockavailable where sid = '{id}'"
                cursor.execute(tempQ)
                x = cursor.fetchall()
                current_count = x[0]['count']
                query = f"UPDATE stockavailable set count = {count+current_count} WHERE sid = '{id}'"
                cursor.execute(query)
                return redirect('/addstock/')
        else:
            # Add stock by file
            import pandas as pd
            from time import sleep
            stockFile = request.FILES['stockFile']
            stocks = pd.read_excel(stockFile)
            for i in range(len(stocks.axes[0])):
                tempRow = []
                for j in range(len(stocks.axes[1])):
                    tempRow.append(stocks.iloc[i,j])
                # If SID not in Database
                if checkSID(tempRow[0]) == False:
                    query = f"insert into stockavailable values('{tempRow[0]}', '{tempRow[1]}', {tempRow[2]}, '{tempRow[3]}', {tempRow[4]}, {tempRow[5]})"
                    cursor.execute(query)
                else:
                    # Already product is available in DB
                    tempQ = f"SELECT count from stockavailable where sid = '{tempRow[0]}'"
                    cursor.execute(tempQ)
                    x = cursor.fetchall()
                    current_count = x[0]['count']
                    query = f"UPDATE stockavailable set count = {tempRow[4]+current_count} WHERE sid = '{tempRow[0]}'"
                    cursor.execute(query)
            sleep(3)
            return redirect('/addstock/')
    else:
        return render(request, 'addstock.html')



def editStock(request):
    cursor.execute("SELECT * FROM stockavailable")
    stocks = cursor.fetchall()
    context = {
        'stocks_data': stocks
    }
    if request.method == "POST":
        id = request.POST['sid'].lower()
        price = request.POST['price'].lower()
        
        query = f"SELECT sid from stockavailable"
        cursor.execute(query)
        flag = False
        list_of_sids = cursor.fetchall()
        # flag is False, if no sid found
        for dict in list_of_sids:
            if dict['sid'] == id:
                flag = True
                break
        if flag == False:
            return HttpResponse("<h1>Item is not found in the database</h1>")
        else:
            cursor.execute(f"UPDATE stockavailable set price = {price} WHERE sid = '{id}'")
            return redirect('/editstock/')
    return render(request, 'editstock.html', context)

def bill(request):
    global incIndex, scanned_products
    #translator = Translator(from_lang = 'en', to_lang='te')
    cursor.execute('Select pname from stockavailable where count > 0')
    temp = cursor.fetchall()
    pnames = []
    for dict in temp:
        #res = translator.translate(dict['pname'])
        pnames.append(dict['pname'])
    
    content = {
        "products" : pnames,
    }

    # Store Stock available data in the JSON file

    cursor.execute("SELECT sid,pname, price FROM stockavailable")
    stocks = cursor.fetchall()

    with open("static/js/stocks1.json", "w") as outfile:
        dump(stocks, outfile, default=str)

    outfile.close()

    # If user clicks the save button, post method will activate
    if request.method == "POST":
        phno = request.POST['num']
        gender = request.POST.get('gender', 0)
        if phno != '':
            gd.phno = phno
            # check if phno already exists or not
            query = f"SELECT * from customers where phno = '{phno}'"
            cursor.execute(query)
            res = cursor.fetchall()
            if(len(res) == 0):
                query = f"INSERT INTO customers values({int(phno)}, '{gender}', 'normal')"
                cursor.execute(query)

        # Call Barcode Scanner
        else:
            id = input("scan : ").strip()
            cursor.execute(f"SELECT * from stockavailable where sid='{id}'")
            res = cursor.fetchone()
            res['total'] = res['price'] - res['save']
            res['incIndex'] = 'x' + str(incIndex)
            scanned_products.append(res)
            content['scanned_products'] = scanned_products
            incIndex += 1
            return render(request, 'bill.html', content)
            # import os
            # import socketio

            # async_mode = None
            # basedir = os.path.dirname(os.path.realpath(__file__))
            # sio = socketio.Server(async_mode=async_mode)


            # # this function is called whenever a client is connected to the server.
            # @sio.event
            # def connect(sid, environ):
            #     sio.emit("response", {"message": "Welcome!"}, room=sid)

    return render(request, 'bill.html', content)

def splitString(s):
    res = []
    l = s.split(',')
    for x in l:
        res.append(x)
    # convert numbers to float
    res[2] = int(res[2])
    res[3] = float(res[3])
    res[4] = float(res[4])
    res[5] = float(res[5])
    return res

def calculations(data):
    ans = {}
    total, save = 0, 0
    for row in data:
        total += row[-1]
        save += row[-2]
    ans['total'] = total
    ans['save'] = save
    return ans

def get_token():
    q = "select count(id) from pipeline"
    cursor.execute(q)
    res = cursor.fetchall()
    return res[0]['count(id)']+1


def print_bill(request):
    global incIndex, scanned_products
    incIndex = 1
    scanned_products = []
    try:
        f = open(Filepath, 'r')
    except FileNotFoundError:
        return HttpResponse("<h1>Save The transaction before billing</h1>")
    # COntents is list of list
    contents = f.readlines()
    for index in range(len(contents)):
        print(contents)
        contents[index] = contents[index].replace('\n', '')
        contents[index] = splitString(contents[index])
    res = calculations(contents)
    content = {
        "print_data" : contents,
        "total" : res['total'],
        "save" : res['save'],
        "uname" : gd.uname
    }

    # add data to transactions table
    from datetime import datetime
    obj = datetime.now()
    date = obj.strftime("%Y-%m-%d")
    time = obj.strftime("%X")
    token = get_token()
    billno = "SN" + date.replace('-', '') + str(token)
    content["bill_no"] = billno
    content['date'] = date
    content['time'] = time
    for index in range(len(contents)):
        # Reduce stock from stock available
        # Already product is available in DB
        tempQ = f"SELECT count from stockavailable where sid = '{contents[index][0]}'"
        cursor.execute(tempQ)
        x = cursor.fetchall()
        if(len(x) != 0):
            current_count = x[0]['count']
            qnty = contents[index][2]
            if(current_count - qnty >= 0):
                query = f"UPDATE stockavailable set count = {current_count - qnty} WHERE sid = '{contents[index][0]}'"
                cursor.execute(query)
                query = f"INSERT INTO transactions values({int(gd.phno)}, '{date}', '{time}', '{billno}', '{contents[index][0]}', '{contents[index][1]}', \
                    {contents[index][2]}, {contents[index][3]}, {contents[index][4]}, {contents[index][5]})"
                cursor.execute(query)
            else:
                os.remove(Filepath)
                return HttpResponse("<h1>Stock is less than required </h1>")
        else:
            os.remove(Filepath)
            return HttpResponse("<h1>Enter Valid Id for Item.</h1>")
        

    
    # check whether day is today or yesterday
    # check the date of last transaction in pipeline, if current date and its date is same, add transaction to the pipeline or drop pipeline
    cursor.execute("SELECT transdate from pipeline limit 1")
    res1 = cursor.fetchall()
    if(len(res1) != 0 and date.strip() != str(res1[0]['transdate'])):
        print('date : ', date)
        print('transdate : ', res1[0]['transdate'])
        cursor.execute("DELETE FROM pipeline")
    else:
        # add data to pipeline table

        query = f"INSERT INTO pipeline values({token}, '{billno}', '{date}', '{time}', {res['total']}, 'no')"
        cursor.execute(query)
    
    return render(request, 'print-bill.html', content)

def deleteTempFile(request):
    os.remove(Filepath)
    return redirect('/accountant/bill.html/')



def logout(request):
    gd.uname = ''
    gd.passw = ''
    gd.phno = ''
    gd.role = ''
    global scanned_products
    scanned_products = []
    return redirect('/login/')
