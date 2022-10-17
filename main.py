from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cars_companies.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    hq = db.Column(db.String(250), nullable=False)
    ceo = db.Column(db.String(100), nullable=False)
    cars = db.relationship('Cars', backref='company')

    def __init__(self, name, hq, ceo):
        self.name = name
        self.hq = hq
        self.ceo = ceo

    def __repr__(self):
        return f"Company - {self.name}"


class Cars(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    price_lks = db.Column(db.Float, unique=True, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))

    def __init__(self, name, price_lks, company_id):
        self.name = name
        self.price_lks = price_lks
        self.company_id = company_id

    def __repr__(self):
        return f"Cars : {self.name}, Price : {self.price_lks}, Company : {self.company_id}"


db.create_all()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/addNewCompany', methods=["POST"])
def add_new_company():
    content_type = request.headers.get("Content-type")
    if content_type == 'application/json':
        new_company = Company(name=request.json['name'], hq=request.json['hq'],
                              ceo=request.json['ceo'])

        db.session.add(new_company)
        db.session.commit()

        return f"Added {new_company.name} to the table."


@app.route('/addnewcar', methods=["POST"])
def add_new_car():
    content_type = request.headers.get("Content-type")
    if content_type == "application/json":

        company_id = request.json['company_id']
        company = Company.query.get(company_id)
        if company is None:
            return "Error: Company not found"
        else:
            new_car = Cars(name=request.json['name'], price_lks=request.json['price_in_lacs'],
                           company_id=company_id)
            company.cars.append(new_car)
            db.session.commit()

            return jsonify(status="Done accurately")


@app.route("/getcarandcompany", methods=["POST"])
def get_car_and_company():
    content_type = request.headers.get("Content-type")
    if content_type == "application/json":
        company_name = request.json["company_name"]
        cars_for_company = Company.query.filter_by(name=company_name).first()
        cars = cars_for_company.cars
        car_name = []
        for car in cars:
            car_name.append(car.name)
        return jsonify(cars=car_name)


@app.route('/updateCompanyDetails', methods=['PATCH'])
def update_company_details():
    content_type = request.headers.get("Content-type")
    if content_type == "application/json":
        name = request.json['name']
        hq_updated = request.json['hq']
        ceo_updated = request.json['ceo']
        company_to_update = Company.query.filter_by(name=name).first()
        company_to_update.hq = hq_updated
        company_to_update.ceo = ceo_updated

        return jsonify(company_name = name,
                       hq = company_to_update.hq,
                       status = "Successfully completed")

@app.route('/updateCarDetails', methods=['PATCH'])
def update_car_details():
    content_type = request.headers.get("Content-type")
    if content_type == "application/json":
        name = request.json['name']
        price_updated = request.json['price_lks']
        company_id_updated = request.json['company_id']
        car_to_update = Cars.query.filter_by(name=name).first()
        car_to_update.price_lks = price_updated
        car_to_update.company_id = company_id_updated

        return jsonify(car_name = name,
                       price = car_to_update.price_lks,
                       company_id = car_to_update.company_id,
                       status = "Successfully completed")

@app.route("/deletecar", methods = ['DELETE'])
def delete_cars():
    car_name = request.json['name']
    car_to_delete = Cars.query.filter_by(name = car_name).first()
    db.session.delete(car_to_delete)
    db.session.commit()
    return " Successfully delete"

@app.route("/deletecompany", methods = ['DELETE'])
def delete_company():
    company_name = request.json['name']
    company_to_delete = Company.query.filter_by(name= company_name).first()
    db.session.delete(company_to_delete)
    db.session.commit()
    return f"Successfully deleted {company_to_delete.name}"



if __name__ == "__main__":
    app.run(debug=True)
