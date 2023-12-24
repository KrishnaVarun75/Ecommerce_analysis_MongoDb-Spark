from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017/')
db = client['ecommerce']
collection = db['project']

# Sample data for dropdowns
sample_cities = ['osasco', 'campos dos goytacazes', 'nova friburgo', 'porto velho', 'montes claros', 'sao goncalo do amarante', 'uberlandia', 'gravatai', 'ribeirao preto', 'lagoa dos gatos', 'maragogi', 'salvador', 'belo jardim', 'cascavel', 'recife', 'aracaju', 'marilia', 'guacui', 'itu', 'jaboatao dos guararapes', 'vitoria', 'maceio', 'rio de janeiro']
sample_states = ['AC', 'AL', 'AM', 'AP', 'BA',
  'CE', 'DF', 'ES', 'GO', 'MA',
  'MG', 'MS', 'MT', 'PA', 'PB',
  'PE', 'PI', 'PR', 'RJ', 'RN',
  'RO', 'RR', 'RS', 'SC', 'SE',
  'SP', 'TO']
sample_payment_types = [ 'boleto', 'credit_card', 'debit_card', 'voucher' ]
sample_product_category = ['agro_industry_and_commerce',
  'air_conditioning',
  'art',
  'arts_and_craftmanship',
  'audio',
  'auto',
  'baby',
  'bed_bath_table',
  'books_general_interest',
  'books_imported',
  'books_technical',
  'cds_dvds_musicals',
  'christmas_supplies',
  'cine_photo',
  'computers',
  'computers_accessories',
  'consoles_games',
  'construction_tools_construction',
  'construction_tools_lights',
  'construction_tools_safety',
  'cool_stuff',
  'costruction_tools_garden',
  'costruction_tools_tools',
  'diapers_and_hygiene',
  'drinks',
  'dvds_blu_ray',
  'electronics',
  'fashio_female_clothing',
  'fashion_bags_accessories',
  'fashion_childrens_clothes',
  'fashion_male_clothing',
  'fashion_shoes',
  'fashion_sport',
  'fashion_underwear_beach',
  'fixed_telephony',
  'flowers',
  'food',
  'food_drink',
  'furniture_bedroom',
  'furniture_decor',
  'furniture_living_room',
  'furniture_mattress_and_upholstery',
  'garden_tools',
  'health_beauty',
  'home_appliances',
  'home_appliances_2',
  'home_comfort_2',
  'home_confort',
  'home_construction',
  'housewares',
  'industry_commerce_and_business',
  'kitchen_dining_laundry_garden_furniture',
  'la_cuisine',
  'luggage_accessories',
  'market_place',
  'music',
  'musical_instruments',
  'office_furniture',
  'party_supplies',
  'perfumery',
  'pet_shop',
  'security_and_services',
  'signaling_and_security',
  'small_appliances',
  'small_appliances_home_oven_and_coffee',
  'sports_leisure',
  'stationery','tablets_printing_image',
  'telephony',
  'toys',
  'watches_gifts']
sample_seller_city = ['abadia dos dourados',
  'abadiania',
  'abaete',
  'abaetetuba',
  'abaiara',
  'abaira',
  'abare',
  'abatia',
  'abdon batista',
  'abelardo luz',
  'abrantes',
  'abre campo',
  'abreu e lima',
  'acaiaca',
  'acailandia',
  'acajutiba',
  'acarau',
  'acari',
  'acegua',
  'acopiara',
  'acreuna',
  'acu',
  'acucena',
  'adamantina',
  'adhemar de barros',
  'adolfo',
  'adrianopolis',
  'adustina',
  'afogados da ingazeira',
  'afonso claudio',
  'afranio',
  'agisse',
  'agrolandia',
  'agronomica',
  'agua boa',
  'agua branca',
  'agua clara',
  'agua comprida',
  'agua doce',
  'agua doce do norte',
  'agua fria de goias',
  'agua limpa',
  'agua nova',
  'agua preta',] 
sample_seller_state = ['AC', 'AM', 'BA', 'CE',
  'DF', 'ES', 'GO', 'MA',
  'MG', 'MS', 'MT', 'PA',
  'PB', 'PE', 'PI', 'PR',
  'RJ', 'RN', 'RO', 'RS',
  'SC', 'SE', 'SP']
sample_order_statuses = ['approved','canceled','delivered','invoiced','processing','shipped','unavailable']



@app.route('/')
def index():
    return render_template(
        'index.html',
        cities=sample_cities,
        states=sample_states,
        payment_types=sample_payment_types,
        p_category = sample_product_category,
        s_cities = sample_seller_city ,
        s_states = sample_seller_state,
        order_statuses=sample_order_statuses
    )

@app.route('/add_data', methods=['POST'])
def add_data():
    data = request.form.to_dict()
    
    # Convert specific fields to numbers
    float_fields = ['payment', 'price_MRP']  # Add other fields as needed
    int_fields=['quantity','rating','payment_installments']
    for field in float_fields:
        if field in data:
            try:
                data[field] = float(data[field])  # Change to float if expecting decimal numbers
            except ValueError:
                pass  # Handle non-numeric values gracefully
    for field in int_fields:
        if field in data:
            try:
                data[field] = int(data[field])  # Change to float if expecting decimal numbers
            except ValueError:
                pass  # Handle non-numeric values gracefully
    
    existing_order = collection.find_one({'order_id': data['order_id']})
    if existing_order:
        return jsonify({'message': 'Order ID already exists. Please enter a different ID.'}), 400
    print(data)
    collection.insert_one(data)
    return jsonify({'message': 'Data added successfully'})

@app.route('/dashboard')
def dashboard():
    data = list(collection.find({}, {'_id': 0}))
    return render_template('dashboard.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
