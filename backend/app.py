from dotenv import load_dotenv
from flask import Flask, request, jsonify
import os
import psycopg2

app = Flask(__name__)

# Loads the environment variabls you should declare in ./.env
# That file is ignored by Git so you can put user-specific or sensitive data there
load_dotenv()

#Database connections
conn = psycopg2.connect(

    # We use environment variables so your credentials are 
    # loaded automatically from your .env file
    dbname = os.getenv('DBNAME'),
    user = os.getenv('DBUSER'),
    password = os.getenv('DBPASSWORD'),
    host = os.getenv('DBHOST'),
    port = os.getenv('DBPORT')
)

@app.route('/organization', methods=['GET', 'POST'])
def handle_organization():
    try:
        cur = conn.cursor()

        match request.method:
            case 'GET':
                cur.execute('SELECT * FROM organization;')
                organizations = cur.fetchall()

                result = []

                for org in organizations:
                    result.append({
                        'organization_name': org[0],
                        'profile': org[1],
                        'organization_card': org[2]
                    })
                
                return jsonify(result), 200
            case 'POST':
                cur.execute(f"INSERT INTO organization VALUES ('{request.form['organization_name']}', '{request.form['profile']}', '{request.form['organization_card']}')")
                conn.commit()

                return 201

    except Exception as e:
        return f"Error: {e}"
            

if __name__ == '__main__':
    app.run(debug=True)