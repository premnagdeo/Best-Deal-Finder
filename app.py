import scraper
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)


@app.route("/check_connection", methods=['GET', 'POST'])
def check_connection():
    return jsonify({'status': 'OK'})


website_dictionary_mapping = {
    'amazon_checkbox': 'search_amazon',
    'flipkart_checkbox': 'search_flipkart',
    'mdcomputers_checkbox': 'search_mdcomputers',
    'neweggindia_checkbox': 'search_neweggindia',
    'primeabgb_checkbox': 'search_primeabgb',
    'theitdepot_checkbox': 'search_theitdepot'
}


@app.route("/data", methods=["POST"])
def scrape():
    if request.form is not None:
        form_data = request.form.to_dict()
        if form_data is not None:
            search_query = form_data['search_query']
            search_count = form_data['search_count']
            name = form_data['name']
            if name in website_dictionary_mapping:
                search_website = 'scraper.' + website_dictionary_mapping[name] + '(' + "'" + search_query + "'" + ', ' + search_count + ')'
                # Call the search function
                data = eval(search_website)

                return data, 200
        else:
            return jsonify({'error': 'No form data'}), 503
    else:
        return jsonify({'error': 'No form found in request'}), 503


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=False, threaded=True)
