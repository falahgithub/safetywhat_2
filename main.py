from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit 



app = Flask(__name__)   
socketio = SocketIO(app)                                              # create the app
                                              # create the app
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sensors.db"        # configure the SQLite database
db = SQLAlchemy()                                                     # create the extension
db.init_app(app)                                                      # initialize the app with the extension

class sensordata(db.Model):                                           # make schema for table creation
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(255), unique=True, nullable=False)
    temp = db.Column(db.Integer)
    pres = db.Column(db.Integer)
    hum = db.Column(db.Integer)

    
with app.app_context():                                               # create table 
    db.create_all()

city= ["Mumbai", "Chennai", "Kochi"]                                  # Initial dummy data 
temp = [35,36,34]
pres= [100,101,102]
hum= [51,49,50]

with app.app_context():                                               # Add initial data in database
    try:
        for i in range(3):
            data = sensordata( city=city[i], temp=temp[i], pres=pres[i], hum=hum[i])
            db.session.add(data)
            db.session.commit()
    except:
        pass


city_entered = None

def to_list(engine):
    listofrows = []
    row = []
    for item in engine:
        row.append(item.city)
        row.append(item.temp)
        row.append(item.pres)
        row.append(item.hum)
        listofrows.append(row)
        row = []
    return(listofrows)

@app.route("/")                                                       # Home route 
def home():   
    print("in home") 
    return render_template("index.html")


@socketio.on("update_data")
def update_data(additional_data):
    i = 4
    while i<5:
        print(f"additional data {additional_data}")
        order_entered = additional_data["sortacc"]
        city_entered = additional_data["filteracc"].title()

        if city_entered: 
            all_data = db.session.execute(db.select(sensordata).order_by(order_entered).filter_by(city=city_entered)).scalars()
        else:
            all_data = db.session.execute(db.select(sensordata).order_by(order_entered)).scalars()
        print("hello")
        all_data_list = to_list(all_data)
        i +=1

        emit("update_data", all_data_list)



@app.route("/add", methods=["GET","POST"])                            # Add route
def add():
    if request.method == "POST":
        try:
                                                                      # Create Record
            if request.form["entered_city"]:
                
                new_data = sensordata(
                    city=request.form["entered_city"].title(),
                    temp=request.form["entered_temp"],
                    pres=request.form["entered_pres"],
                    hum=request.form["entered_hum"])
                
                db.session.add(new_data)
                db.session.commit()
        except:
            pass
        finally:            
            return redirect(url_for('home'))
        
    return render_template("add.html")

@app.route("/update", methods=["GET", "POST"])                        # Update route
def update():
    if request.method == "POST":
        try:
                                                                      # Update record
            cityname = request.form["entered_city"].title()
            record  = db.session.execute(db.select(sensordata).filter_by(city=cityname)).scalar_one()
        
            if request.form["entered_temp"]:     record.temp = request.form["entered_temp"] 
            if request.form["entered_pres"]:     record.pres = request.form["entered_pres"] 
            if request.form["entered_hum"]:      record.hum = request.form["entered_hum"] 
        
            db.session.commit()

        except:
            pass
        
        finally:
            return redirect(url_for("home"))
    
    return render_template("update.html")


if __name__=='__main__':
    app.run(debug=True)
  