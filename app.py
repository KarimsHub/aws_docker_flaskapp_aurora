from flask import Flask, request, jsonify
import os
import boto3 
from botocore.config import Config

app = Flask(__name__)

my_config = Config(
    region_name = 'eu-central-1'
)
rds_data = boto3.client('rds-data', config=my_config, aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.environ.get('AWS_SECRET_ACESS_KEY'))

#Database Configuration Items
aurora_db_name = os.environ.get('DB_NAME') #os.environ['DB_NAME']
aurora_cluster_arn = os.environ.get('CLUSTER_ARN') #os.environ['CLUSTER_ARN']
aurora_secret_arn = os.environ.get('SECRET_ARN') #os.environ['SECRET_ARN']

@app.route('/getPerson') # API 1 - getPerson
def getPerson():
    personId = request.args.get('personId') #extracting the personId from the request
    response = callDbWithStatement("SELECT * FROM Persons WHERE personId='" + str(personId) + "'" )
    person = {} #storing the created response object
    records = response['records'] #extracting the records array out of the response
    for record in records:
        person['personId'] = record[0]['longValue'] # serial = longvalue
        person['firstName'] = record[1]['stringValue'] # varchar = stringvalue
        person['lastName'] = record[2]['stringValue']
    print(person)
    return jsonify(person)

@app.route('/createPerson',  methods=['POST']) # API 2 - createPerson
def createPerson():
    request_data = request.get_json()
    personId = str(request_data['personId'])
    firstName = request_data['firstName']
    lastName = request_data['lastName']
    callDbWithStatement("INSERT INTO Persons(personId, firstName, lastName) VALUES ('" 
    + personId + "', '" + firstName + "', '" + lastName + "');")
    return ""
    
def callDbWithStatement(statement):
    response = rds_data.execute_statement(  #using the data client from boto3 and calling the execute statement api
            database = aurora_db_name,
            resourceArn = aurora_cluster_arn,
            secretArn = aurora_secret_arn,
            sql = statement,
            includeResultMetadata = True
        )
    print("Making Call " + statement)
    print(response) #Delete this in production
    return response

if __name__ == '__main__':
    app.run(threaded=True,host='0.0.0.0',port=8081)