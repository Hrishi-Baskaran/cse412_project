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

@app.route('/organization', methods=['GET', 'POST', 'DELETE', 'PUT'])
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
            case 'DELETE':

                params = []
                conditions = []
                paper_id = request.form.get('organization_name', None)
                profile = request.form.get('profile', None)
                org_card = request.form.get('organization_card', None)
                
                if paper_id is not None:
                    conditions.append('organization_name = %s')
                    params.append(paper_id)
                if profile is not None:
                    conditions.append('profile = %s')
                    params.append(profile)
                if org_card is not None:
                    conditions.append('organization_card = %s')
                    params.append(org_card)

                print("qurying")
                query = "DELETE FROM organization WHERE " + " AND ".join(conditions)

                if (len(params) > 0):
                    cur.execute(query, tuple(params))
                    cnt = cur.rowcount
                    conn.commit()
                    return f"Deleted {cnt} users", 200
                else:
                    return "No deletion criterion provided", 400
            case 'PUT':
                params = []
                update_statements = []

                paper_id = request.form.get('organization_name', None)
                profile = request.form.get('profile', None)
                org_card = request.form.get('organization_card', None)

                if paper_id == None:
                    return "Name of organization to update not specified", 400
                
                if profile is not None:
                    update_statements.append('profile = %s')
                    params.append(profile)
                if org_card is not None:
                    update_statements.append('organization_card = %s')
                    params.append(org_card)

                query = "UPDATE organization SET " + ", ".join(update_statements)

                print(query)

                if len(params) > 0:
                    cur.execute(query, tuple(params))
                    cnt = cur.rowcount
                    conn.commit()
                    return f"Updated {cnt} users", 200
                else:
                    return "No update values provided", 200

                
                


                
                

    except Exception as e:
        return f"Error: {e}"
            

@app.route('/cites', methods=['GET', 'POST', 'DELETE', 'PUT'])
def handle_cites():
    try:
        cur = conn.cursor()

        match request.method:
            case 'GET':
                cur.execute('SELECT * FROM cites;')
                citations = cur.fetchall()

                result = []

                for cite in citations:
                    result.append({
                        'paper_id': cite[0],
                        'model_id': cite[1]
                    })
                
                return jsonify(result), 200

            case 'POST':
                cur.execute(f"INSERT INTO cites VALUES ('{request.form['paper_id']}', '{request.form['model_id']}')")
                conn.commit()

                return 201
            case 'DELETE':

                params = []
                conditions = []
                paper_id = request.form.get('paper_id', None)
                model_id = request.form.get('model_id', None)
                
                if paper_id is not None:
                    conditions.append('paper_id = %s')
                    params.append(paper_id)
                if model_id is not None:
                    conditions.append('model_id = %s')
                    params.append(model_id)

                query = "DELETE FROM cites WHERE " + " AND ".join(conditions)

                if (len(params) > 0):
                    cur.execute(query, tuple(params))
                    cnt = cur.rowcount
                    conn.commit()
                    return f"Deleted {cnt} citations", 200
                else:
                    return "No deletion criterion provided", 400
                


                
                

    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    app.run(debug=True)