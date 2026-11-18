"""
NEXORA Electronics synthetic ERP data generator
================================================
Populates the existing 33-table PostgreSQL schema with fictional, connected
Indian electronics-retail data from 2016-08-01 through 2018-08-31.

Install: pip install psycopg2-binary

Set DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD environment variables,
then run: python generate_python_generator.py

The script refuses to duplicate existing data. Use --truncate only if you
intentionally want to empty all 33 tables before regenerating them.
"""

import os
import sys
import random
import calendar
import hashlib
import argparse
from datetime import date, datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP
import psycopg2
from psycopg2.extras import execute_values

START = date(2016, 8, 1)
END = date(2018, 8, 31)  # Both August months included
SEED = 42
rng = random.Random(SEED)

CUSTOMERS = 1800
EMPLOYEES = 72
VENDORS = 40
BASE_ORDERS_MONTH = 240
PURCHASES_MONTH = 24
BATCH = 1000

TABLES = [
    "chart_of_accounts","companies","branches","customers","departments",
    "journals","journal_entries","journal_items","leads","product_categories",
    "products","bills_of_materials","bom_items","sales_opportunities",
    "sales_orders","invoices","payments","sales_order_items","users",
    "employees","attendance","payrolls","vendors","purchase_orders","bills",
    "bill_payments","purchase_order_items","warehouses","inventory_stocks",
    "inventory_transactions","production_orders","work_centers",
    "production_routing"
]

BRANCHES = [
    ("Kochi Main Branch","MG Road, Kochi, Kerala","+91-484-4001001"),
    ("Kozhikode Branch","Mavoor Road, Kozhikode","+91-495-4001002"),
    ("Bengaluru Branch","Indiranagar, Bengaluru","+91-80-4001003"),
    ("Chennai Branch","T Nagar, Chennai","+91-44-4001004"),
    ("Hyderabad Branch","Ameerpet, Hyderabad","+91-40-4001005"),
    ("Mumbai Branch","Andheri East, Mumbai","+91-22-4001006"),
]
DEPARTMENTS = ["Sales","Finance","Human Resources","Procurement",
               "Warehouse Operations","Customer Service","IT Operations"]
FIRST = ["Aarav","Aditya","Aisha","Ananya","Arjun","Diya","Farhan","Ishaan",
         "Kavya","Kiran","Meera","Mohammed","Neha","Nikhil","Priya","Rahul",
         "Riya","Rohan","Sana","Sneha","Vikram","Akhil","Amal","Divya",
         "Fathima","Hari","Maya","Naveen","Pooja","Sanjay","Varun","Zoya"]
LAST = ["Nair","Menon","Sharma","Reddy","Iyer","Khan","Thomas","Pillai",
        "Patel","Verma","Das","Rao","Mehta","Joseph","Kulkarni","Shetty",
        "Kapoor","Mishra","Gupta","Bhat"]
CITIES = [("Kochi","Kerala"),("Kozhikode","Kerala"),("Thrissur","Kerala"),
          ("Bengaluru","Karnataka"),("Chennai","Tamil Nadu"),
          ("Hyderabad","Telangana"),("Mumbai","Maharashtra"),
          ("Pune","Maharashtra"),("Delhi","Delhi"),("Coimbatore","Tamil Nadu")]
STREETS = ["MG Road","Market Road","Park Street","Lake View Road",
           "Station Road","Civil Lines","Temple Road","Ring Road","Main Road"]

CATALOG = {
"Laptops":[("AsterBook 14 i5 Laptop",52000,78000),("AsterBook Ryzen Laptop",43000,65000),("NexPro Ultrabook",68000,105000),("NexPro Performance Laptop",75000,125000),("Orbit Student Laptop",29000,42000),("Vertex Gaming Laptop",78000,145000),("CoreLite Business Laptop",48000,72000),("NovaBook Laptop",35000,56000),("Nexora Workstation Laptop",95000,155000)],
"Smartphones":[("Nova X1 Smartphone",12000,18000),("Nova X2 Plus Smartphone",18000,26000),("Orbit M5 Smartphone",9000,14500),("Vertex Pro Smartphone",28000,42000),("Aster Note Smartphone",16000,24000),("Core One Smartphone",7000,11000),("Nexora Edge Smartphone",32000,48000),("Pulse Max Smartphone",22000,34000),("Nova Lite Smartphone",6000,9500)],
"Televisions":[("Vision 32 LED TV",15000,22000),("Vision 40 Full HD TV",23000,32000),("Vision 43 Smart TV",28000,42000),("Vision 50 4K Smart TV",42000,65000),("Vision 55 UHD TV",52000,78000),("Aster 32 Smart TV",18000,27000),("Orbit 43 LED TV",24000,35000),("Nexora 49 4K TV",39000,59000),("Vision 65 Premium TV",85000,125000)],
"Audio":[("Pulse Bluetooth Speaker",1800,4500),("Pulse Wireless Headphones",2200,6500),("Aster Soundbar",6500,14000),("Orbit Home Theatre",9000,22000),("Core Wired Earphones",350,1200),("Nova Wireless Earbuds",1800,5200),("Vertex Studio Headphones",4500,9500),("Nexora Party Speaker",7500,16000),("Pulse Portable Radio",900,2400)],
"Cameras":[("Aster DSLR Camera",32000,58000),("Orbit Mirrorless Camera",48000,85000),("Nova Compact Camera",12000,22000),("Vertex Action Camera",9000,18000),("Nexora Digital Camera",18000,32000),("Aster 50mm Lens",6500,14000),("Aster 18-55mm Lens",4500,9500),("Orbit Camcorder",24000,42000),("Nova HD Webcam",1800,4500)],
"Tablets":[("Nova Tab 7",6500,11000),("Nova Tab 10",11000,18000),("Aster Tab Plus",18000,28000),("Orbit Business Tablet",22000,35000),("Nexora Study Tablet",8500,14500),("Vertex Pro Tablet",28000,42000),("Core Mini Tablet",5500,9500),("Aster Note Tablet",15000,24000),("Nova Kids Tablet",4500,8000)],
"Storage":[("Core 500GB External HDD",2800,4200),("Core 1TB External HDD",3500,5500),("Core 2TB External HDD",5200,7800),("Nova 128GB USB Drive",450,850),("Nova 256GB USB Drive",800,1400),("Aster 120GB SSD",1800,3000),("Aster 240GB SSD",2800,4500),("Vertex 480GB SSD",4800,7200),("Core 64GB Memory Card",450,900)],
"Networking":[("Orbit Wireless Router",1800,3500),("Core Dual Band Router",2800,5200),("Nexora Gigabit Switch",3200,6500),("Vertex WiFi Adapter",650,1500),("Aster 8 Port Switch",1400,2800),("Orbit ADSL Modem",900,1800),("Core Network Cable",350,850),("Nexora Access Point",3500,7000),("Vertex Range Extender",1200,2600)],
"Accessories":[("Nexora Laptop Bag",700,1800),("Core Wireless Mouse",450,1200),("Aster Mechanical Keyboard",1800,4500),("Nova USB-C Charger",500,1500),("Orbit HDMI Cable",250,750),("Vertex Laptop Stand",650,1600),("Nexora Power Bank",900,2600),("Core Webcam",1200,3200),("Aster Cooling Pad",700,1800)],
"Components":[("Core Desktop Processor",6500,18000),("Aster Desktop Motherboard",4500,12000),("Nova 8GB DDR4 RAM",1800,3200),("Nova 16GB DDR4 RAM",3200,5800),("Vertex 1TB Internal HDD",2800,4500),("Core 500GB SSD",3000,5200),("Aster 22 Inch Monitor",6500,11000),("Orbit Desktop Power Supply",1800,3800),("Nexora Custom Desktop PC",42000,68000)]
}
SEASON = {1:1.10,2:.96,3:1.04,4:.94,5:1.08,6:1.10,7:.98,8:1.02,9:1.12,10:1.32,11:1.38,12:1.15}

def M(x):
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def rand_date(a,b):
    return a + timedelta(days=rng.randint(0,(b-a).days))

def months():
    d=date(START.year,START.month,1)
    while d<=END:
        yield d
        d=date(d.year+1,1,1) if d.month==12 else date(d.year,d.month+1,1)

def mend(d):
    return date(d.year,d.month,calendar.monthrange(d.year,d.month)[1])

def workday(a,b):
    d=rand_date(a,b)
    if d.weekday()==6: d += timedelta(days=1)
    if d>b: d -= timedelta(days=1)
    return d

def person():
    return rng.choice(FIRST),rng.choice(LAST)

def address():
    city,state=rng.choice(CITIES)
    return f"{rng.randint(1,220)}, {rng.choice(STREETS)}, {city}"[:36]

def phone():
    return "+91-"+str(rng.randint(6000000000,9999999999))

def ref(prefix,n):
    return f"{prefix}{n:07d}"[:9]

def ins(cur,table,cols,rows):
    if not rows: return
    names=", ".join('"'+c+'"' for c in cols)
    execute_values(cur,f'INSERT INTO public."{table}" ({names}) VALUES %s',rows,page_size=BATCH)

def add_entry(entries,items,jid,journal_id,dt,description,debit_acc,credit_acc,amount):
    amount=M(amount)
    if amount<=0: return jid
    entries.append((jid,description[:500],dt,journal_id,ref("JE",jid)))
    # journal_items column order is: id, account_id, credit, debit, journal_entry_id
    items.append((len(items)+1,debit_acc,M(0),amount,jid))
    items.append((len(items)+2,credit_acc,amount,M(0),jid))
    return jid+1

def make_master():
    accounts=[
      ("1000","Cash and Bank","assets"),("1100","Accounts Receivable","assets"),
      ("1200","Inventory Asset","assets"),("1300","Office Equipment","assets"),
      ("2000","Accounts Payable","liabilities"),("2100","Statutory Deductions Payable","liabilities"),
      ("3000","Owner Equity","equity"),("4000","Product Sales Revenue","revenue"),
      ("4100","Sales Discounts","revenue"),("5000","Cost of Goods Sold","expenses"),
      ("5100","Employee Salary Expense","expenses"),("5200","Rent Expense","expenses"),
      ("5300","Utilities Expense","expenses"),("5400","Marketing Expense","expenses"),
      ("5500","Delivery and Operating Expense","expenses")]
    data={}
    data["chart_of_accounts"]=[(i+1,*x) for i,x in enumerate(accounts)]
    data["companies"]=[(1,"2nd Floor, MG Road, Kochi","accounts@nexora.example",
                        "NEXORA Electronics Pvt. Ltd.","+91-484-4001000","32AABCN1234F1Z5")]
    data["branches"]=[(i+1,a,1,n,p) for i,(n,a,p) in enumerate(BRANCHES)]
    depts=[]; deptmap={}; did=1
    for bid in range(1,7):
        for name in DEPARTMENTS:
            depts.append((did,bid,name)); deptmap[(bid,name)]=did; did+=1
    data["departments"]=depts
    cats=list(CATALOG)
    data["product_categories"]=[(i+1,"Consumer electronics: "+n.lower(),n) for i,n in enumerate(cats)]
    catids={n:i+1 for i,n in enumerate(cats)}
    products=[]; pmeta={}; pid=1
    for cat,items in CATALOG.items():
        for name,lo,hi in items:
            price=M(rng.randint(lo,hi)); cost=M(price*Decimal(str(rng.uniform(.72,.88))))
            products.append((pid,f"890{rng.randint(1000000000,9999999999)}",catids[cat],cost,name[:80],price,f"NX{pid:07d}"))
            pmeta[pid]={"name":name,"category":cat,"price":price,"cost":cost}; pid+=1
    data["products"]=products
    vendors=[]
    vendor_names=["Prime Digital Distributors","SouthTech Wholesale","Orbit Electronics Supply","Vertex Mobile Distribution","BluePeak Computers","Metro AV Supplies","National IT Components","NextWave Devices","CoreLink Technologies","Apex Consumer Electronics","BrightStar Trading","DigitalHub Wholesale","Sapphire Telecom Supplies","Zenith Computer Products","Reliable Electronics India","Pioneer Tech Distributors","Nova Components Pvt Ltd","Crescent Digital Supply","Westline Electronics","Eastern Tech Traders","Unified Devices India","SmartSource Distributors","Citywide Computer Supply","Innotech Wholesale","PrimeVision Electronics","A1 Mobile Traders","FutureLink Systems","Evergreen IT Supplies","Global Gadget Distributors","Silverline Electronics","TechBridge India","MicroCore Distributors","Starline Digital Products","ValueTech Wholesale","Crown Electronics Supply","Nexus Device Traders","Rapid Retail Supplies","Spectrum Tech India","Central Computer Distributors","ProConnect Electronics"]
    for i,n in enumerate(vendor_names,1):
        f,l=person(); vendors.append((i,address(),f+" "+l,f"vendor{i:03d}@nexora.example",n,phone()))
    data["vendors"]=vendors
    data["warehouses"]=[(i+1,i+1,f"Warehouse, {BRANCHES[i][0].split()[0]}",f"NEXORA {BRANCHES[i][0]} Warehouse") for i in range(6)]
    data["journals"]=[(1,"J001","Sales Journal"),(2,"J002","Purchase Journal"),(3,"J003","Cash and Bank Journal"),(4,"J004","Payroll Journal"),(5,"J005","General Journal")]
    data["work_centers"]=[(1,M(450),"Desktop Configuration"),(2,M(550),"Hardware Quality Testing"),(3,M(350),"Packaging and Dispatch Preparation")]
    data["meta"]={"deptmap":deptmap,"pmeta":pmeta,"accounts":{"bank":1,"ar":2,"inventory":3,"ap":5,"sales":8,"cogs":10,"salary":11}}
    return data

def make_customers():
    rows=[]
    for i in range(1,CUSTOMERS+1):
        f,l=person(); rows.append((i,address(),f"{f.lower()}.{l.lower()}.{i}@example.com",f"{f} {l}",phone()))
    return rows

def make_staff(deptmap):
    users=[]; employees=[]; meta={}
    roles={"Sales":"sales","Finance":"fin","Human Resources":"hr","Procurement":"buyer","Warehouse Operations":"ops","Customer Service":"cs","IT Operations":"admin"}
    for i in range(1,EMPLOYEES+1):
        branch=(i-1)%6+1; dept=DEPARTMENTS[(i-1)%len(DEPARTMENTS)]
        f,l=person(); email=f"{f.lower()}.{l.lower()}.{i}@nexora.example"
        users.append((i,deptmap[(branch,dept)],email,hashlib.md5(f"demo-{i}".encode()).hexdigest(),roles[dept],f"{f.lower()}.{l.lower()}.{i}"))
        hired=rand_date(START,END-timedelta(days=20))
        if i<=20: hired=rand_date(START,START+timedelta(days=30))
        salary=M(rng.randint(18000,95000))
        employees.append((i,f,hired,l,salary,i)); meta[i]={"hire":hired,"salary":salary}
    return users,employees,meta

def make_leads():
    leads=[]; opp=[]
    for cid in range(1,CUSTOMERS+1):
        if rng.random()<.38:
            lid=len(leads)+1
            leads.append((lid,cid,M(rng.randint(5000,180000)),rng.choice(["website","walk-in","referral","social_media","advertisement","phone","email"]),rng.choice(["new","qualified","converted","lost"])))
            if rng.random()<.72:
                opp.append((len(opp)+1,rand_date(START,END),lid,rng.choice(["qualified","proposal","negotiation","won","lost"]),f"Electronics opportunity - customer {cid}"))
    return leads,opp

def make_procurement(pmeta,balances,invtx,accounts):
    pos=[]; poitems=[]; bills=[]; billpays=[]; entries=[]; jitems=[]; jid=1; poid=1; billid=1; bpid=1; txid=len(invtx)+1
    for month in months():
        for _ in range(PURCHASES_MONTH):
            dt=workday(month,min(mend(month),END)); branch=rng.randint(1,6); vendor=rng.randint(1,VENDORS)
            selected=rng.sample(list(pmeta),rng.randint(2,5)); lines=[]; total=M(0)
            for p in selected:
                q=rng.randint(8,35); cost=M(pmeta[p]["cost"]*Decimal(str(rng.uniform(.94,1.04))))
                line=M(cost*q); lines.append((p,q,cost)); total+=line
            status=rng.choices(["received","cancelled"],[94,6])[0]
            pos.append((poid,branch,dt,status,M(total),vendor))
            for p,q,c in lines: poitems.append((len(poitems)+1,p,poid,Decimal(q),c))
            if status!="cancelled":
                receipt=min(dt+timedelta(days=rng.randint(1,8)),END)
                for p,q,c in lines:
                    balances[(p,branch)]+=q
                    invtx.append((txid,p,Decimal(q),datetime.combine(receipt,time(11)),"purchase_receipt",branch)); txid+=1
                bd=min(receipt+timedelta(days=rng.randint(0,5)),END); due=bd+timedelta(days=30)
                ratio=rng.choices([1,.5,0],[72,18,10])[0]; paid=M(total*Decimal(str(ratio)))
                bstatus="paid" if ratio==1 else ("partial" if ratio else ("overdue" if due<END else "pending"))
                bills.append((billid,bd,due,poid,bstatus,M(total),vendor))
                jid=add_entry(entries,jitems,jid,2,bd,f"Supplier bill for purchase order {poid}",3,5,total)
                if paid:
                    pd=min(bd+timedelta(days=rng.randint(3,25)),END)
                    billpays.append((bpid,accounts["bank"],paid,billid,pd,rng.choice(["bank_transfer","NEFT","RTGS","cheque"])))
                    jid=add_entry(entries,jitems,jid,3,pd,f"Payment against supplier bill {billid}",5,1,paid); bpid+=1
                billid+=1
            poid+=1
    return pos,poitems,bills,billpays,invtx,balances,entries,jitems,jid

def make_sales(pmeta,balances,invtx,accounts):
    orders=[]; items=[]; invoices=[]; payments=[]; entries=[]; jitems=[]; jid=1; oid=iid=payid=1; txid=len(invtx)+1
    for mi,month in enumerate(months()):
        count=int(BASE_ORDERS_MONTH*(1+.018*mi)*SEASON[month.month])
        for _ in range(count):
            dt=workday(month,min(mend(month),END)); branch=rng.randint(1,6); customer=rng.randint(1,CUSTOMERS)
            chosen=rng.choices(list(pmeta),weights=[2.4 if pmeta[p]["category"] in ("Smartphones","Accessories","Laptops") else 1 for p in pmeta],k=rng.randint(1,3))
            lines=[]; total=M(0); cogs=M(0)
            for p in chosen:
                q=rng.choices([1,2,3],[75,20,5])[0]; price=pmeta[p]["price"]
                discount=M(price*q*Decimal(str(rng.choices([0,.03,.05,.08,.10],[50,15,20,10,5])[0])))
                line=M(price*q-discount); lines.append((p,q,price,discount)); total+=line; cogs+=pmeta[p]["cost"]*q
            total=M(total); cogs=M(cogs)
            status=rng.choices(["completed","shipped","pending","cancelled"],[72,17,8,3])[0]
            orders.append((oid,branch,customer,dt,status,total))
            for p,q,price,discount in lines: items.append((len(items)+1,discount,p,Decimal(q),oid,price))
            if status!="cancelled":
                for p,q,price,discount in lines:
                    balances[(p,branch)]-=q
                    invtx.append((txid,p,Decimal(q),datetime.combine(dt,time(15)),"sale_dispatch",branch)); txid+=1
                due=dt+timedelta(days=30)
                choice=rng.choices(["full","partial","none"],[68,22,10])[0]
                paid=total if choice=="full" else (M(total*Decimal(str(rng.uniform(.25,.75))) if choice=="partial" else 0))
                istatus="paid" if choice=="full" else ("partial" if choice=="partial" else ("overdue" if due<END else "pending"))
                invoices.append((iid,customer,due,dt,oid,istatus,total))
                jid=add_entry(entries,jitems,jid,1,dt,f"Sales invoice {iid} for order {oid}",2,8,total)
                jid=add_entry(entries,jitems,jid,1,dt,f"Cost of goods sold for order {oid}",10,3,cogs)
                if paid:
                    pd=min(dt+timedelta(days=rng.randint(1,24)),END)
                    payments.append((payid,accounts["bank"],paid,iid,pd,rng.choice(["UPI","card","bank_transfer","cash","net_banking","debit_card"])))
                    jid=add_entry(entries,jitems,jid,3,pd,f"Customer payment for invoice {iid}",1,2,paid); payid+=1
                iid+=1
            oid+=1
    return orders,items,invoices,payments,invtx,balances,entries,jitems

def make_hr(staffmeta):
    attendance=[]; payroll=[]; entries=[]; jitems=[]; jid=1; aid=1; pid=1
    for eid,meta in staffmeta.items():
        d=max(meta["hire"],START)
        while d<=END:
            if d.weekday()!=6 and rng.random()<.94:
                h=rng.choices([8,9,10],[15,70,15])[0]
                cin=datetime.combine(d,time(h,rng.randint(0,59)))
                cout=cin+timedelta(hours=rng.choices([7,8,9,10],[8,60,25,7])[0],minutes=rng.randint(0,45))
                attendance.append((aid,cin,cout,eid,d)); aid+=1
            d+=timedelta(days=1)
        m=date(max(meta["hire"],START).year,max(meta["hire"],START).month,1)
        while m<=END:
            start=max(m,meta["hire"],START); finish=min(mend(m),END)
            gross=meta["salary"]; net=M(gross*(1-Decimal(str(rng.uniform(.04,.12)))))
            payroll.append((pid,eid,gross,net,finish,start))
            entries.append((jid,f"Monthly payroll for employee {eid}",finish,4,ref("JE",jid)))
            jitems.extend([(len(jitems)+1,11,M(0),gross,jid),(len(jitems)+2,1,net,M(0),jid)])
            diff=M(gross-net)
            if diff: jitems.append((len(jitems)+1,6,diff,M(0),jid))
            jid+=1; pid+=1
            idx=m.month-1+1; m=date(m.year+idx//12,idx%12+1,1)
    return attendance,payroll,entries,jitems

def make_expenses():
    entries=[]; items=[]; jid=1
    for m in months():
        dt=min(mend(m),END)
        for branch in range(1,7):
            for account,desc,lo,hi in [(12,"Branch rent",45000,85000),(13,"Utilities and internet",5000,14000),(14,"Marketing",8000,30000),(15,"Delivery and operations",6000,18000)]:
                amount=M(rng.randint(lo,hi))
                jid=add_entry(entries,items,jid,5,dt,f"{desc} - branch {branch}",account,1,amount)
    return entries,items

def make_production(pmeta):
    finished=[p for p,v in pmeta.items() if v["name"]=="Nexora Custom Desktop PC"]
    components=[p for p,v in pmeta.items() if v["category"]=="Components" and p not in finished]
    boms=[]; bomitems=[]
    for p in finished:
        bid=len(boms)+1; boms.append((bid,p,Decimal("1.0")))
        for component in rng.sample(components,4):
            bomitems.append((len(bomitems)+1,bid,component,Decimal(rng.choice([1,1,2]))))
    orders=[]; routing=[]; oid=1
    for m in months():
        for _ in range(rng.randint(1,4)):
            start=workday(m,min(mend(m),END)); finish=min(start+timedelta(days=rng.randint(1,4)),END)
            orders.append((oid,finish,rng.choice(finished),Decimal(rng.randint(2,12)),start,"completed",rng.randint(1,6)))
            for seq,wc in enumerate([1,2,3],1):
                routing.append((len(routing)+1,oid,M(rng.uniform(.5,2.5)),seq,M(rng.uniform(.2,.8)),wc))
            oid+=1
    return boms,bomitems,orders,routing

def count_rows(cur,table):
    cur.execute(f'SELECT COUNT(*) FROM public."{table}"')
    return cur.fetchone()[0]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--truncate",action="store_true",help="Empty all 33 tables before generating data.")
    args=parser.parse_args()
    cfg={"host":os.getenv("DB_HOST","localhost"),"port":int(os.getenv("DB_PORT","5432")),
         "dbname":os.getenv("DB_NAME","NEXORA_DATABASE"),"user":os.getenv("DB_USER","postgres"),
         "password":os.getenv("DB_PASSWORD","")}
    if not cfg["password"]:
        import getpass
        cfg["password"]=getpass.getpass("PostgreSQL password: ")
    print("Connecting to PostgreSQL...")
    conn=psycopg2.connect(**cfg)
    try:
        conn.autocommit=False
        with conn.cursor() as cur:
            if args.truncate:
                cur.execute("TRUNCATE TABLE "+", ".join('public."'+t+'"' for t in TABLES)+" RESTART IDENTITY CASCADE")
            else:
                populated=[f"{t}: {count_rows(cur,t)}" for t in TABLES if count_rows(cur,t)>0]
                if populated:
                    print("These tables are not empty; no records inserted:")
                    print("\n".join(populated))
                    print("Use --truncate only if you intend to replace existing data.")
                    conn.rollback(); return

        print("Preparing company, branches, departments, products and accounts...")
        data=make_master(); meta=data["meta"]; pmeta=meta["pmeta"]; accounts=meta["accounts"]
        data["customers"]=make_customers()
        users,employees,staffmeta=make_staff(meta["deptmap"])
        data["users"]=users; data["employees"]=employees
        leads,opps=make_leads(); data["leads"]=leads; data["sales_opportunities"]=opps

        # Opening stock at every product/warehouse combination.
        balances={}; invtx=[]; txid=1
        for p in pmeta:
            for w in range(1,7):
                qty=rng.randint(80,145); balances[(p,w)]=qty
                invtx.append((txid,p,Decimal(qty),datetime.combine(START,time(8)),"opening",w)); txid+=1

        print("Generating purchase orders, suppliers' bills and payments...")
        pos,poitems,bills,billpays,invtx,balances,pentries,pitems,pjid=make_procurement(pmeta,balances,invtx,accounts)
        print("Generating sales orders, invoices, payments and stock movements...")
        orders,orderitems,invoices,payments,invtx,balances,sentries,sitems=make_sales(pmeta,balances,invtx,accounts)
        print("Generating employee attendance and monthly payroll...")
        attendance,payroll,hentries,hitems=make_hr(staffmeta)
        print("Generating operating expenses and light device-configuration activity...")
        eentries,eitems=make_expenses()
        boms,bomitems,prodorders,routing=make_production(pmeta)

        # Re-number journal entry IDs and journal-item IDs globally.
        journal_entries=[]; journal_items=[]; next_jid=1; next_item=1
        for es,its in [(pentries,pitems),(sentries,sitems),(hentries,hitems),(eentries,eitems)]:
            remap={}
            for e in es:
                remap[e[0]]=next_jid
                journal_entries.append((next_jid,e[1],e[2],e[3],ref("JE",next_jid)))
                next_jid+=1
            for it in its:
                journal_items.append((next_item,it[1],it[2],it[3],remap[it[4]]))
                next_item+=1

        stocks=[]
        for (p,w),qty in sorted(balances.items()):
            if qty<0: raise ValueError(f"Negative stock: product {p}, warehouse {w}: {qty}")
            stocks.append((len(stocks)+1,p,Decimal(qty),w))

        data.update({
          "purchase_orders":pos,"purchase_order_items":poitems,"bills":bills,"bill_payments":billpays,
          "sales_orders":orders,"sales_order_items":orderitems,"invoices":invoices,"payments":payments,
          "attendance":attendance,"payrolls":payroll,"bills_of_materials":boms,"bom_items":bomitems,
          "production_orders":prodorders,"production_routing":routing,
          "inventory_transactions":invtx,"inventory_stocks":stocks,
          "journal_entries":journal_entries,"journal_items":journal_items
        })

        specs=[
        ("chart_of_accounts","id code name type"),("companies","id address email name phone tax_number"),
        ("branches","id address company_id name phone"),("customers","id address email name phone"),
        ("departments","id branch_id name"),("journals","id code name"),
        ("product_categories","id description name"),("products","id barcode category_id cost name price sku"),
        ("vendors","id address contact_name email name phone"),("warehouses","id branch_id location name"),
        ("work_centers","id hourly_cost name"),("users","id department_id email password_hash role username"),
        ("employees","id first_name hire_date last_name salary user_id"),
        ("leads","id customer_id estimated_value source status"),
        ("sales_opportunities","id close_date lead_id stage title"),
        ("bills_of_materials","id product_id quantity"),("bom_items","id bom_id component_product_id quantity"),
        ("purchase_orders","id branch_id order_date status total_amount vendor_id"),
        ("purchase_order_items","id product_id purchase_order_id quantity unit_cost"),
        ("bills","id bill_date due_date purchase_order_id status total_amount vendor_id"),
        ("bill_payments","id account_id amount bill_id payment_date payment_method"),
        ("sales_orders","id branch_id customer_id order_date status total_amount"),
        ("sales_order_items","id discount product_id quantity sales_order_id unit_price"),
        ("invoices","id customer_id due_date invoice_date sales_order_id status total_amount"),
        ("payments","id account_id amount invoice_id payment_date payment_method"),
        ("attendance","id check_in check_out employee_id work_date"),
        ("payrolls","id employee_id gross_salary net_salary period_end period_start"),
        ("production_orders","id end_date product_id quantity start_date status warehouse_id"),
        ("production_routing","id production_order_id run_time sequence setup_time work_center_id"),
        ("inventory_transactions","id product_id quantity transaction_date transaction_type warehouse_id"),
        ("inventory_stocks","id product_id quantity warehouse_id"),
        ("journal_entries","id description entry_date journal_id reference"),
        ("journal_items","id account_id credit debit journal_entry_id")]
        print("Inserting data into PostgreSQL (single transaction)...")
        with conn.cursor() as cur:
            for table,columns in specs:
                cols=columns.split()
                rows=data.get(table,[])
                ins(cur,table,cols,rows)
                print(f"{table:<28} {len(rows):>9,}")
            # Set identity sequences to the maximum explicit ID.
            for table in TABLES:
                cur.execute(f"SELECT setval(pg_get_serial_sequence('public.{table}', 'id'), COALESCE(MAX(id),1), COUNT(*)>0) FROM public.{table}")
            print("\nFinal row counts:")
            total=0
            for table in TABLES:
                n=count_rows(cur,table); total+=n
                print(f"{table:<28} {n:>9,}")
            print("-"*42)
            print(f"{'TOTAL':<28} {total:>9,}")
        conn.commit()
        print(f"\nSUCCESS. NEXORA data covers {START} through {END}.")
        print("All generated records are synthetic. Review business assumptions before production use.")
    except Exception as exc:
        conn.rollback()
        print("\nFAILED. The database transaction was rolled back.")
        print(exc)
        raise
    finally:
        conn.close()

if __name__=="__main__":
    main()
