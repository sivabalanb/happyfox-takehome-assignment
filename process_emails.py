import json
import mysql.connector
from app import mark_email_read_or_unread, move_message

def connect_to_mysql(host, user, password, database):
    try:
        # Create a connection to the MySQL database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            print("Connected to MySQL database")

        return connection

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def close_mysql_connection(connection):
    # Close the connection to the MySQL database
    if connection.is_connected():
        connection.close()
        print("Connection to MySQL database closed")

def read_json(file_path):
    try:
        # Read JSON data from the file
        with open(file_path, 'r') as file:
            json_data = json.load(file)
        return json_data

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in file {file_path}: {e}")
        return None
  
def validate_rules_in_database(rules, predicates,  database_connection):

    cursor = database_connection.cursor()
    # Base Query
    query = "SELECT id FROM assignment.mail WHERE "

    # Iterate through rules and build the query
    for rule in rules:
        field = rule['field']
        predicate = rule['predicate']
        value = rule['value']
        # Updating query based on the predicate
        if predicate == 'Contains':
            query += f"{field} LIKE '%{value}%' {predicates} "
        elif predicate == 'less than':
            query += f"{field} < '{value}' {predicates} "
        else:
            print(f"Logging the rule for now as its not going to be processed")
        # Can add more conditions based on other predicates

    # Remove the trailing predicate
    query = query.rstrip(f' {predicates} ')
    print(f'Query to be executed - {query}')
    # Execute the query
    cursor.execute(query)

    # Fetch the results
    result = cursor.fetchall()

    # Extract message_id from the results
    message_ids = [row[0] for row in result]

    return message_ids

def main():
    # Read JSON data
    rules_data = read_json("rules.json")

    if rules_data:
        # Access individual elements
        predicates = 'AND' if rules_data.get('predicates') == 'All' else 'OR'
        rules = rules_data.get('rules')
        action = rules_data.get('action')
    
    # Replace with your actual MySQL database details
    host = "localhost"
    user = "root"
    password = "password"
    database = "assignment"
    
    # Connect to MySQL
    db_connection = connect_to_mysql(host, user, password, database)

    # Validate rules in the database
    matching_message_ids = validate_rules_in_database(rules, predicates,  db_connection)

    # Print the matching message IDs
    print("Matching Message IDs:", matching_message_ids)

    for message_id in matching_message_ids:
        if action == "Mark as read":
            mark_email_read_or_unread(message_id, True)
        if action == "Mark as unread":
            mark_email_read_or_unread(message_id, False)
        if action == "Move Message":
            move_message(message_id, "INBOX")
    # Close the connection when done
    close_mysql_connection(db_connection)

if __name__ == "__main__":
    main()
