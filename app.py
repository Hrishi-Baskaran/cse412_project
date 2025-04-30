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
            
# person
@app.route('/person', methods=['GET', 'POST', 'DELETE', 'PUT'])
def handle_person():
    # only these columns can be used as filters or in updates
    valid_cols = {"person_id", "huggingface_username", "github_link"}

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
                # huggingface_username is required
                if 'huggingface_username' not in data:
                    return jsonify({'error': 'huggingface_username required'}), 400

                # insert a new person, return the new person_id
                cur.execute(
                    'INSERT INTO person '
                    '(huggingface_username, person_description, github_link) '
                    'VALUES (%s, %s, %s) RETURNING person_id',
                    (
                        data['huggingface_username'],
                        data.get('person_description'),
                        data.get('github_link')
                    )
                )
                pid = cur.fetchone()[0]
                return jsonify({'person_id': pid}), 201

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

if __name__ == '__main__':
    app.run(debug=True)