import json
import boto3
import os
from boto3.dynamodb.types import TypeSerializer

# Initialize clients
db_client = boto3.client('dynamodb')

# Environment variables
DEPLOY_NAME = os.environ.get("DEPLOY_NAME", "nadialin")

def putTableItem(tableName, item):
    # Add item data to table        
    try:
        response = db_client.put_item(
            TableName=tableName,
            Item=item
        )
        return response
    except Exception as e:
        return str(e)

def json_to_dynamodb(json_data):
        serializer = TypeSerializer()
        return {key: serializer.serialize(value) for key, value in json_data.items()}

def backupEvent(data):
    try:
        tables = {
            "events":None,
            "hunters":None,
            "squads":None,
            "machines":None,
            "instances":None,
            "services":None
        }
        for t in tables.keys():
            try:
                tables[t] = data[t]
                for i in tables[t]:
                    putTableItem(DEPLOY_NAME+'-'+t, json_to_dynamodb(i))
            except Exception as e:
                # Assume ResourceNotFoundException
                tables[t] = {}
        return tables
    except Exception as e:
        return

def lambda_handler(event, context=None):
    # AWS Lambda handler for API Gateway v2 (supports only POST)
    print("Received event:", json.dumps(event, indent=2))
    return( backupEvent(event.get('body')) )

if __name__ == "__main__":
    tables_TestData = {
        'events': [{'name':'testEvent', "startTime":"20251231T00:00:00Z"}], 
        'hunters': [
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Battleaxe@test.com", "name": "Battleaxe", "sub": "not-real", "squad": "Alligator"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Blowgun@test.com", "name": "Blowgun", "sub": "not-real", "squad": "Badger"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Chainsaw@test.com", "name": "Chainsaw", "sub": "not-real", "squad": "Bat"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Club@test.com", "name": "Club", "sub": "not-real", "squad": "Beaver"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Crossbowhand@test.com", "name": "Crossbowhand", "sub": "not-real", "squad": "Bear"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Crossbowheavy@test.com", "name": "Crossbowheavy", "sub": "not-real", "squad": "Bobcat"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Crossbowlight@test.com", "name": "Crossbowlight", "sub": "not-real", "squad": "Bumblebee"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Dagger@test.com", "name": "Dagger", "sub": "not-real", "squad": "Buffalo"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Dart@test.com", "name": "Dart", "sub": "not-real", "squad": "Butterfly"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Drone@test.com", "name": "Drone", "sub": "not-real", "squad": "Cougar"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Flail@test.com", "name": "Flail", "sub": "not-real", "squad": "Cow"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Flamethrower@test.com", "name": "Flamethrower", "sub": "not-real", "squad": "Crocodile"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Glaive@test.com", "name": "Glaive", "sub": "not-real", "squad": "Coyote"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Greataxe@test.com", "name": "Greataxe", "sub": "not-real", "squad": "Crow"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Greatclub@test.com", "name": "Greatclub", "sub": "not-real", "squad": "Deer"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Greatsword@test.com", "name": "Greatsword", "sub": "not-real", "squad": "Dolphin"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Grenade@test.com", "name": "Grenade", "sub": "not-real", "squad": "Dog"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Halberd@test.com", "name": "Halberd", "sub": "not-real", "squad": "Dogfish"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Handaxe@test.com", "name": "Handaxe", "sub": "not-real", "squad": "Dove"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Javelin@test.com", "name": "Javelin", "sub": "not-real", "squad": "Dragonfly"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Knife@test.com", "name": "Knife", "sub": "not-real", "squad": "Eagle"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Lance@test.com", "name": "Lance", "sub": "not-real", "squad": "Elk"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Lighthammer@test.com", "name": "Lighthammer", "sub": "not-real", "squad": "Falcon"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Longbow@test.com", "name": "Longbow", "sub": "not-real", "squad": "Fox"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Longsword@test.com", "name": "Longsword", "sub": "not-real", "squad": "Frog"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Mace@test.com", "name": "Mace", "sub": "not-real", "squad": "GrizzlyBear"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "MachineGun@test.com", "name": "MachineGun", "sub": "not-real", "squad": "Halibut"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Maul@test.com", "name": "Maul", "sub": "not-real", "squad": "Hawk"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Morningstar@test.com", "name": "Morningstar", "sub": "not-real", "squad": "Heron"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Musket@test.com", "name": "Musket", "sub": "not-real", "squad": "Horse"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Net@test.com", "name": "Net", "sub": "not-real", "squad": "KillerWhale"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Nunchucks@test.com", "name": "Nunchucks", "sub": "not-real", "squad": "Kingfisher"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Pike@test.com", "name": "Pike", "sub": "not-real", "squad": "Lizard"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Pistol@test.com", "name": "Pistol", "sub": "not-real", "squad": "Moose"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Quarterstaff@test.com", "name": "Quarterstaff", "sub": "not-real", "squad": "Mouse"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Rapier@test.com", "name": "Rapier", "sub": "not-real", "squad": "Otter"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Rifle@test.com", "name": "Rifle", "sub": "not-real", "squad": "Owl"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Scimitar@test.com", "name": "Scimitar", "sub": "not-real", "squad": "Raccoon"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Shortbow@test.com", "name": "Shortbow", "sub": "not-real", "squad": "Raven"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Shortsword@test.com", "name": "Shortsword", "sub": "not-real", "squad": "Porcupine"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Shotgun@test.com", "name": "Shotgun", "sub": "not-real", "squad": "Salmon"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Sickle@test.com", "name": "Sickle", "sub": "not-real", "squad": "Seal"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Sling@test.com", "name": "Sling", "sub": "not-real", "squad": "Shark"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Spear@test.com", "name": "Spear", "sub": "not-real", "squad": "Snake"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Tank@test.com", "name": "Tank", "sub": "not-real", "squad": "Spider"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Torpedo@test.com", "name": "Torpedo", "sub": "not-real", "squad": "Squirrel"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Trident@test.com", "name": "Trident", "sub": "not-real", "squad": "Turtle"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "War pick@test.com", "name": "Warpick", "sub": "not-real", "squad": "Weasel"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Warhammer@test.com", "name": "Warhammer", "sub": "not-real", "squad": "Whale"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Whip@test.com", "name": "Whip", "sub": "not-real", "squad": "Wolf"}            
            ], 
        'squads': [
            {'name': 'gooba', 'score': 0},
              {"name": "Whip"}
            ], 
        'machines': [
            {'name': 'nadialin', 'templateName': 'nadialin-base-template', 
             'services': [
                {'name': 'get_flag', 'protocol': 'http', 'expected_return': '{squad}', 'port': 49855, 'url': 'http://{ip}:49855/flag.txt', 'points': 10},
                {"name": "Whip", "protocol": "ssm", "expected_return": "Whip", "url": "Whip@{ip}", "points": 1}
                ],
             'authorNotes': 'interesting text'}], 
        'instances': [{'name':'testInstance'}], 
        'services': [{'name':'testService'}]
    }

    """
    {'events': [{'startTime': {'S': '2017-07-21T17:32:28Z'}, 'homePage': {'S': 'nadialin.kengraf.com'}, 'squadSize': {'N': '1'}, 'endTime': {'S': '2017-07-21T18:32:28Z'}, 'admin': {'S': 'wooba'}, 'name': {'S': 'nadialin'}}], 'hunters': [{'squads': {'S': 'goobas'}, 'admin': {'BOOL': True}, 'email': {'S': 'wooba@gooba.com'}, 'name': {'S': 'wooba'}, 'sub': {'S': 'fakevalue'}}], 'squads': [{'name': {'S': 'goobas'}, 'score': {'N': '0'}}, {'publicKey': {'S': 'fake data'}, 'description': {'S': 'big, furry'}, 'name': {'S': 'bear'}, 'points': {'N': '100'}, 'privateKey': {'S': 'fake data'}}], 'machines': [{'name': {'S': 'nadialin'}, 'templateName': {'S': 'nadialin-base-template'}, 'services': {'L': [{'M': {'name': {'S': 'get_flag'}, 'protocol': {'S': 'http'}, 'expected_return': {'S': '{squad}'}, 'port': {'N': '49855'}, 'url': {'S': 'http://{ip}:49855/flag.txt'}, 'points': {'N': '10'}}}, {'M': {'name': {'S': 'alice_login'}, 'protocol': {'S': 'ssm'}, 'expected_return': {'S': 'alice'}, 'url': {'S': 'alice@{ip}'}, 'points': {'N': '1'}}}]}, 'authorNotes': {'S': 'interesting text'}}], 'instances': [], 'services': []}
    """
    """
    {"event": [], "hunters": [{"email": {"S": "wooba@gooba.com"}, "admin": {"BOOL": True}, "name": {"S": "wooba"}, "sub": {"S": "fakevalue"}, "squads": {"S": "gooba"}}], "squads": [{"name": {"S": "test2"}}, {"name": {"S": "goobas"}, "score": {"N": "0"}}], "machines": [{"name": {"S": "nadialin"}, "templateName": {"S": "nadialin-base-template"}, "services": {"L": [{"M": {"protocol": {"S": "http"}, "port": {"N": "49855"}, "name": {"S": "get_flag"}, "expected_return": {"S": "{squad}"}, "url": {"S": "http://{ip}:49855/{squad}/flag.txt"}, "points": {"N": "1"}}}]}, "authorNotes": {"S": "interesting text"}}], "instances": [], "services": []}
"""

    print( backupEvent(tables_TestData))

