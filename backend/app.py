from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS 

import os
import psycopg2

app = Flask(__name__)
CORS(app)
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
                org_name = request.form['organization_name']
                # check if organization already exists in database
                cur.execute("SELECT * FROM organization WHERE organization_name = %s", (org_name,))
                if cur.fetchone():
                    return jsonify({"error": "Organization already exists"}), 409  # Conflict
                cur.execute(
                    "INSERT INTO organization VALUES (%s, %s, %s)",
                    (org_name, request.form['profile'], request.form['organization_card'])
                )
                conn.commit()
                return jsonify({"message": "Organization created successfully"}), 201
            case 'DELETE':
                data = request.get_json() or {}
                params = []
                conditions = []

                paper_id = data.get('organization_name', None)
                profile = data.get('profile', None)
                org_card = data.get('organization_card', None)
                
                if paper_id is not None:
                    conditions.append('organization_name = %s')
                    params.append(paper_id)
                if profile is not None:
                    conditions.append('profile = %s')
                    params.append(profile)
                if org_card is not None:
                    conditions.append('organization_card = %s')
                    params.append(org_card)

                if len(params) > 0:
                    query = "DELETE FROM organization WHERE " + " AND ".join(conditions)
                    cur.execute(query, tuple(params))
                    cnt = cur.rowcount
                    conn.commit()
                    return jsonify({'message': f'Deleted {cnt} organization(s)'}), 200
                else:
                    return jsonify({'error': 'No deletion criterion provided'}), 400

            case 'PUT':
                data = request.get_json() or {}
                params = []
                update_statements = []

                org_name = data.get('organization_name', None)
                profile = data.get('profile', None)
                org_card = data.get('organization_card', None)

                if org_name is None:
                    return jsonify({'error': 'organization_name is required to identify the record to update'}), 400

                if profile is not None:
                    update_statements.append('profile = %s')
                    params.append(profile)
                if org_card is not None:
                    update_statements.append('organization_card = %s')
                    params.append(org_card)

                if not update_statements:
                    return jsonify({'error': 'No update values provided'}), 400

                query = "UPDATE organization SET " + ", ".join(update_statements) + " WHERE organization_name = %s"
                params.append(org_name)

                cur.execute(query, tuple(params))
                conn.commit()
                cnt = cur.rowcount

                if cnt == 0:
                    return jsonify({'error': 'No organization found with that name'}), 404

                return jsonify({'message': f'Updated {cnt} organization(s)'}), 200


                
                


                
                

    except Exception as e:
        return f"Error: {e}"
            
# person
@app.route('/person', methods=['GET', 'POST', 'DELETE', 'PUT'])
def handle_person():
    # only these columns can be used as filters or in updates
    valid_cols = {"person_id", "huggingface_username", "github_link", "person_description"}

    try:
        with conn, conn.cursor() as cur:

            # GET 
            if request.method == 'GET':
                # collect any valid filters from the query string
                filters = {k: v for k, v in request.args.items() if k in valid_cols}

                base_sql = 'SELECT * FROM person'
                if filters:
                    # build WHERE clause like "col1 = %s AND col2 = %s"
                    clause = ' AND '.join(f"{col} = %s" for col in filters)
                    sql_query = f"{base_sql} WHERE {clause}"
                    cur.execute(sql_query, list(filters.values()))
                else:
                    # no filters, select everything
                    cur.execute(base_sql)

                # fetch column names and rows, convert to list of dicts
                cols = [d.name for d in cur.description]
                rows = [dict(zip(cols, r)) for r in cur.fetchall()]
                return jsonify(rows), 200

            # POST
            if request.method == 'POST':
                data = request.get_json() or {}
                required_fields = {'person_id', 'huggingface_username'}
                # huggingface_username is required
                if any(field not in data for field in required_fields):
                    return jsonify({'error': 'person_id and huggingface_username required'}), 400

                # insert a new person, return the new person_id
                cur.execute(
                    'INSERT INTO person (person_id, huggingface_username, person_description, github_link) '
                    'VALUES (%s, %s, %s, %s)',
                    (
                        data['person_id'],
                        data['huggingface_username'],
                        data.get('person_description'),
                        data.get('github_link')
                    )
                )
                conn.commit()
                return jsonify({'message': 'person inserted successfully'}), 201

            # DELETE
            if request.method == 'DELETE':
                data = request.get_json() or {}
                # only keep keys we allow
                filters = {k: v for k, v in data.items() if k in valid_cols}
                if 'person_id' not in filters:
                    return jsonify({'error': 'person_id is required to delete'}), 400

                # build delete clause
                clause = ' AND '.join(f"{col} = %s" for col in filters)
                cur.execute(
                    f'DELETE FROM person WHERE {clause}',
                    list(filters.values())
                )
                return '', 204

            # PUT
            if request.method == 'PUT':
                data = request.get_json() or {}
                # person_id must be provided to know which row to update
                if 'person_id' not in data:
                    return jsonify({'error': 'person_id required'}), 400

                pid = data.pop('person_id')
                if not data:
                    return jsonify({'error': 'no attributes to update'}), 400
                # ensure only valid columns are being updated
                if any(k not in valid_cols for k in data):
                    return jsonify({'error': 'invalid column'}), 400

                # build SET clause like "col1 = %s, col2 = %s"
                set_clause = ', '.join(f"{col} = %s" for col in data)
                cur.execute(
                    f'UPDATE person SET {set_clause} WHERE person_id = %s',
                    list(data.values()) + [pid]
                )
                return '', 204

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# writes
@app.route('/writes', methods=['GET', 'POST', 'DELETE'])
def handle_writes():
    try:
        with conn, conn.cursor() as cur:
            # GET
            if request.method == 'GET':
                # collect filters if provided in URL ?person_id=…&paper_id=…
                filters = {
                    k: v for k, v in request.args.items()
                    if k in ("person_id", "paper_id")
                }

                base_sql = 'SELECT person_id, paper_id FROM writes'
                if filters:
                    # build WHERE clause like "person_id = %s AND paper_id = %s"
                    clause = ' AND '.join(f"{col} = %s" for col in filters)
                    sql_query = f"{base_sql} WHERE {clause}"
                    cur.execute(sql_query, list(filters.values()))
                else:
                    # no filters → return all rows
                    cur.execute(base_sql)

                rows = [
                    {'person_id': p, 'paper_id': q}
                    for p, q in cur.fetchall()
                ]
                return jsonify(rows), 200

            # POST
            if request.method == 'POST':
                data = request.get_json() or {}
                # ensure both keys are present in the JSON body
                if {'person_id', 'paper_id'} - data.keys():
                    return jsonify({'error': 'person_id and paper_id required'}), 400

                # insert the (person_id, paper_id) pair
                cur.execute(
                    'INSERT INTO writes (person_id, paper_id) VALUES (%s, %s)',
                    (data['person_id'], data['paper_id'])
                )
                return '', 201

            # DELETE 
            if request.method == 'DELETE':
                data = request.get_json() or {}
                # expect JSON {"person_id":X,"paper_id":Y}
                if {'person_id', 'paper_id'} - data.keys():
                    return jsonify({'error': 'person_id and paper_id required'}), 400

                # delete the matching pair
                cur.execute(
                    'DELETE FROM writes WHERE person_id = %s AND paper_id = %s',
                    (data['person_id'], data['paper_id'])
                )
                return '', 204

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# creates
@app.route('/creates', methods=['GET', 'POST', 'DELETE'])
def handle_creates():
    # decide which bridge table to use
    rel_type = request.args.get('type')  # must be 'model' or 'dataset'
    table_map = {
        'model':   'creates_pm',
        'dataset': 'creates_pd'
    }
    table = table_map.get(rel_type)
    if not table:
        return jsonify({'error': 'query param "type" must be model or dataset'}), 400

    try:
        with conn, conn.cursor() as cur:

            # GET
            if request.method == 'GET':
                # pick only person_id and repo_id from the URL
                allowed = ('person_id', 'repo_id')
                filters = {
                    k: v for k, v in request.args.items()
                    if k in allowed
                }

                base_sql = f'SELECT person_id, repo_id FROM {table}'
                if filters:
                    # build WHERE clause "person_id = %s AND repo_id = %s"
                    clause = ' AND '.join(f"{col} = %s" for col in filters)
                    sql_query = f"{base_sql} WHERE {clause}"
                    cur.execute(sql_query, list(filters.values()))
                else:
                    cur.execute(base_sql)

                rows = [
                    {'person_id': p, 'repo_id': r}
                    for p, r in cur.fetchall()
                ]
                return jsonify(rows), 200

            # POST
            if request.method == 'POST':
                # expects JSON {"person_id":X,"repo_id":Y}
                data = request.get_json() or {}
                if {'person_id', 'repo_id'} - data.keys():
                    return jsonify({'error': 'person_id and repo_id required'}), 400

                cur.execute(
                    f'INSERT INTO {table} (person_id, repo_id) VALUES (%s, %s)',
                    (data['person_id'], data['repo_id'])
                )
                return '', 201

            # DELETE
            if request.method == 'DELETE':
                data = request.get_json(force=True) or {}
                # expect JSON {"person_id":X,"repo_id":Y}
                if {'person_id', 'repo_id'} - data.keys():
                    return jsonify({'error': 'person_id and repo_id required'}), 400

                cur.execute(
                    f'DELETE FROM {table} WHERE person_id = %s AND repo_id = %s',
                    (data['person_id'], data['repo_id'])
                )
                return '', 204

    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

# paper endpoint
@app.route('/paper', methods=['GET', 'POST', 'DELETE', 'PUT'])
def handle_paper():
    # valid columns for filtering and updates
    valid_cols = {"paper_id", "title", "abstract", "publication_date"}
    
    try:
        with conn, conn.cursor() as cur:
            
            # GET
            if request.method == 'GET':
                # collect any valid filters from the query string
                filters = {k: v for k, v in request.args.items() if k in valid_cols}
                
                base_sql = 'SELECT * FROM paper'
                if filters:
                    # build WHERE clause
                    clause = ' AND '.join(f"{col} = %s" for col in filters)
                    sql_query = f"{base_sql} WHERE {clause}"
                    cur.execute(sql_query, list(filters.values()))
                else:
                    # no filters, select everything
                    cur.execute(base_sql)
                
                # fetch column names and rows, convert to list of dicts
                cols = [d.name for d in cur.description]
                rows = [dict(zip(cols, r)) for r in cur.fetchall()]
                return jsonify(rows), 200
            
            # POST
            if request.method == 'POST':
                data = request.get_json() or {}
                # title is required
                if 'title' not in data:
                    return jsonify({'error': 'title required'}), 400
                
                # insert a new paper, return the new paper_id
                cur.execute(
                    'INSERT INTO paper '
                    '(paper_id, title, abstract, publication_date) '
                    'VALUES (%s, %s, %s, %s)',
                    (   
                        data['paper_id'],
                        data['title'],
                        data.get('abstract'),
                        data.get('publication_date')
                    )
                )
                return '', 201
            
            # DELETE
            if request.method == 'DELETE':
                data = request.get_json() or {}
                # only keep keys we allow
                filters = {k: v for k, v in data.items() if k in valid_cols}
                if not filters:
                    return jsonify({'error': 'provide at least one filter'}), 400
                
                # build delete clause
                clause = ' AND '.join(f"{col} = %s" for col in filters)
                cur.execute(
                    f'DELETE FROM paper WHERE {clause}',
                    list(filters.values())
                )
                return '', 204
            
            # PUT
            if request.method == 'PUT':
                data = request.get_json() or {}
                # paper_id must be provided to know which row to update
                if 'paper_id' not in data:
                    return jsonify({'error': 'paper_id required'}), 400
                
                pid = data.pop('paper_id')
                if not data:
                    return jsonify({'error': 'no attributes to update'}), 400
                # ensure only valid columns are being updated
                if any(k not in valid_cols for k in data):
                    return jsonify({'error': 'invalid column'}), 400
                
                # build SET clause
                set_clause = ', '.join(f"{col} = %s" for col in data)
                cur.execute(
                    f'UPDATE paper SET {set_clause} WHERE paper_id = %s',
                    list(data.values()) + [pid]
                )
                return '', 204
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# model endpoint
@app.route('/model', methods=['GET', 'POST', 'DELETE', 'PUT'])
def handle_model():
    valid_cols = {"model_id", "model_name", "description", "parameters", "release_date"}
    
    try:
        with conn, conn.cursor() as cur:
            
            # GET
            if request.method == 'GET':
                filters = {k: v for k, v in request.args.items() if k in valid_cols}
                
                base_sql = 'SELECT * FROM model'
                if filters:
                    clause = ' AND '.join(f"{col} = %s" for col in filters)
                    sql_query = f"{base_sql} WHERE {clause}"
                    cur.execute(sql_query, list(filters.values()))
                else:
                    cur.execute(base_sql)
                
                cols = [d.name for d in cur.description]
                rows = [dict(zip(cols, r)) for r in cur.fetchall()]
                return jsonify(rows), 200
            
            # POST
            if request.method == 'POST':
                data = request.get_json() or {}
                if 'model_name' not in data:
                    return jsonify({'error': 'model_name required'}), 400
                
                cur.execute(
                    'INSERT INTO model '
                    '(model_name, description, parameters, release_date) '
                    'VALUES (%s, %s, %s, %s) RETURNING model_id',
                    (
                        data['model_name'],
                        data.get('description'),
                        data.get('parameters'),
                        data.get('release_date')
                    )
                )
                mid = cur.fetchone()[0]
                return jsonify({'model_id': mid}), 201
            
            # DELETE
            if request.method == 'DELETE':
                data = request.get_json() or {}
                filters = {k: v for k, v in data.items() if k in valid_cols}
                if not filters:
                    return jsonify({'error': 'provide at least one filter'}), 400
                
                clause = ' AND '.join(f"{col} = %s" for col in filters)
                cur.execute(
                    f'DELETE FROM model WHERE {clause}',
                    list(filters.values())
                )
                return '', 204
            
            # PUT
            if request.method == 'PUT':
                data = request.get_json() or {}
                if 'model_id' not in data:
                    return jsonify({'error': 'model_id required'}), 400
                
                mid = data.pop('model_id')
                if not data:
                    return jsonify({'error': 'no attributes to update'}), 400
                if any(k not in valid_cols for k in data):
                    return jsonify({'error': 'invalid column'}), 400
                
                set_clause = ', '.join(f"{col} = %s" for col in data)
                cur.execute(
                    f'UPDATE model SET {set_clause} WHERE model_id = %s',
                    list(data.values()) + [mid]
                )
                return '', 204
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# dataset endpoint
@app.route('/dataset', methods=['GET', 'POST', 'DELETE', 'PUT'])
def handle_dataset():
    valid_cols = {"dataset_id", "dataset_name", "description", "size", "release_date"}
    
    try:
        with conn, conn.cursor() as cur:
            
            # GET
            if request.method == 'GET':
                filters = {k: v for k, v in request.args.items() if k in valid_cols}
                
                base_sql = 'SELECT * FROM dataset'
                if filters:
                    clause = ' AND '.join(f"{col} = %s" for col in filters)
                    sql_query = f"{base_sql} WHERE {clause}"
                    cur.execute(sql_query, list(filters.values()))
                else:
                    cur.execute(base_sql)
                
                cols = [d.name for d in cur.description]
                rows = [dict(zip(cols, r)) for r in cur.fetchall()]
                return jsonify(rows), 200
            
            # POST
            if request.method == 'POST':
                data = request.get_json() or {}
                if 'dataset_name' not in data:
                    return jsonify({'error': 'dataset_name required'}), 400
                
                cur.execute(
                    'INSERT INTO dataset '
                    '(dataset_name, description, size, release_date) '
                    'VALUES (%s, %s, %s, %s) RETURNING dataset_id',
                    (
                        data['dataset_name'],
                        data.get('description'),
                        data.get('size'),
                        data.get('release_date')
                    )
                )
                did = cur.fetchone()[0]
                return jsonify({'dataset_id': did}), 201
            
            # DELETE
            if request.method == 'DELETE':
                data = request.get_json() or {}
                filters = {k: v for k, v in data.items() if k in valid_cols}
                if not filters:
                    return jsonify({'error': 'provide at least one filter'}), 400
                
                clause = ' AND '.join(f"{col} = %s" for col in filters)
                cur.execute(
                    f'DELETE FROM dataset WHERE {clause}',
                    list(filters.values())
                )
                return '', 204
            
            # PUT
            if request.method == 'PUT':
                data = request.get_json() or {}
                if 'dataset_id' not in data:
                    return jsonify({'error': 'dataset_id required'}), 400
                
                did = data.pop('dataset_id')
                if not data:
                    return jsonify({'error': 'no attributes to update'}), 400
                if any(k not in valid_cols for k in data):
                    return jsonify({'error': 'invalid column'}), 400
                
                set_clause = ', '.join(f"{col} = %s" for col in data)
                cur.execute(
                    f'UPDATE dataset SET {set_clause} WHERE dataset_id = %s',
                    list(data.values()) + [did]
                )
                return '', 204
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# cities endpoint
@app.route('/cities', methods=['GET', 'POST', 'DELETE', 'PUT'])
def handle_cities():
    valid_cols = {"city_id", "city_name", "country", "latitude", "longitude", "population"}
    
    try:
        with conn, conn.cursor() as cur:
            
            # GET
            if request.method == 'GET':
                filters = {k: v for k, v in request.args.items() if k in valid_cols}
                
                base_sql = 'SELECT * FROM cities'
                if filters:
                    clause = ' AND '.join(f"{col} = %s" for col in filters)
                    sql_query = f"{base_sql} WHERE {clause}"
                    cur.execute(sql_query, list(filters.values()))
                else:
                    cur.execute(base_sql)
                
                cols = [d.name for d in cur.description]
                rows = [dict(zip(cols, r)) for r in cur.fetchall()]
                return jsonify(rows), 200
            
            # POST
            if request.method == 'POST':
                data = request.get_json() or {}
                if 'city_name' not in data or 'country' not in data:
                    return jsonify({'error': 'city_name and country required'}), 400
                
                cur.execute(
                    'INSERT INTO cities '
                    '(city_name, country, latitude, longitude, population) '
                    'VALUES (%s, %s, %s, %s, %s) RETURNING city_id',
                    (
                        data['city_name'],
                        data['country'],
                        data.get('latitude'),
                        data.get('longitude'),
                        data.get('population')
                    )
                )
                cid = cur.fetchone()[0]
                return jsonify({'city_id': cid}), 201
            
            # DELETE
            if request.method == 'DELETE':
                data = request.get_json() or {}
                filters = {k: v for k, v in data.items() if k in valid_cols}
                if not filters:
                    return jsonify({'error': 'provide at least one filter'}), 400
                
                clause = ' AND '.join(f"{col} = %s" for col in filters)
                cur.execute(
                    f'DELETE FROM cities WHERE {clause}',
                    list(filters.values())
                )
                return '', 204
            
            # PUT
            if request.method == 'PUT':
                data = request.get_json() or {}
                if 'city_id' not in data:
                    return jsonify({'error': 'city_id required'}), 400
                
                cid = data.pop('city_id')
                if not data:
                    return jsonify({'error': 'no attributes to update'}), 400
                if any(k not in valid_cols for k in data):
                    return jsonify({'error': 'invalid column'}), 400
                
                set_clause = ', '.join(f"{col} = %s" for col in data)
                cur.execute(
                    f'UPDATE cities SET {set_clause} WHERE city_id = %s',
                    list(data.values()) + [cid]
                )
                return '', 204
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)