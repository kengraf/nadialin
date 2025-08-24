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
        'events': [{'name':'testEvent'}], 
        'hunters': [
            {'uuid': '5ce7a5ad-f02f-41ea-9ea1-6ca80d5c9d98', 'pictureBytes': 'https://lh3.googleusercontent.com/a/ACg8ocLQ3brj76ujujP8i5s21BMGS4w4p3_tzTperrtJdtTNQlJKIc9a=s96-c', 'email': 'kengraf57@gmail.com', 'name': 'kengraf57', 'sub': '115804770028255050984', 'squad': 'bear'},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Battleaxe@test.com", "name": "Battleaxe", "sub": "115804770028255050984", "squad": "Alligator"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Blowgun@test.com", "name": "Blowgun", "sub": "115804770028255050984", "squad": "Badger"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Chainsaw@test.com", "name": "Chainsaw", "sub": "115804770028255050984", "squad": "Bat"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Club@test.com", "name": "Club", "sub": "115804770028255050984", "squad": "Beaver"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Crossbowhand@test.com", "name": "Crossbowhand", "sub": "115804770028255050984", "squad": "Bear"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Crossbowheavy@test.com", "name": "Crossbowheavy", "sub": "115804770028255050984", "squad": "Bobcat"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Crossbowlight@test.com", "name": "Crossbowlight", "sub": "115804770028255050984", "squad": "Bumblebee"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Dagger@test.com", "name": "Dagger", "sub": "115804770028255050984", "squad": "Buffalo"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Dart@test.com", "name": "Dart", "sub": "115804770028255050984", "squad": "Butterfly"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Drone@test.com", "name": "Drone", "sub": "115804770028255050984", "squad": "Cougar"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Flail@test.com", "name": "Flail", "sub": "115804770028255050984", "squad": "Cow"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Flamethrower@test.com", "name": "Flamethrower", "sub": "115804770028255050984", "squad": "Crocodile"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Glaive@test.com", "name": "Glaive", "sub": "115804770028255050984", "squad": "Coyote"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Greataxe@test.com", "name": "Greataxe", "sub": "115804770028255050984", "squad": "Crow"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Greatclub@test.com", "name": "Greatclub", "sub": "115804770028255050984", "squad": "Deer"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Greatsword@test.com", "name": "Greatsword", "sub": "115804770028255050984", "squad": "Dolphin"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Grenade@test.com", "name": "Grenade", "sub": "115804770028255050984", "squad": "Dog"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Halberd@test.com", "name": "Halberd", "sub": "115804770028255050984", "squad": "Dogfish"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Handaxe@test.com", "name": "Handaxe", "sub": "115804770028255050984", "squad": "Dove"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Javelin@test.com", "name": "Javelin", "sub": "115804770028255050984", "squad": "Dragonfly"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Knife@test.com", "name": "Knife", "sub": "115804770028255050984", "squad": "Eagle"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Lance@test.com", "name": "Lance", "sub": "115804770028255050984", "squad": "Elk"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Lighthammer@test.com", "name": "Lighthammer", "sub": "115804770028255050984", "squad": "Falcon"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Longbow@test.com", "name": "Longbow", "sub": "115804770028255050984", "squad": "Fox"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Longsword@test.com", "name": "Longsword", "sub": "115804770028255050984", "squad": "Frog"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Mace@test.com", "name": "Mace", "sub": "115804770028255050984", "squad": "GrizzlyBear"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "MachineGun@test.com", "name": "MachineGun", "sub": "115804770028255050984", "squad": "Halibut"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Maul@test.com", "name": "Maul", "sub": "115804770028255050984", "squad": "Hawk"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Morningstar@test.com", "name": "Morningstar", "sub": "115804770028255050984", "squad": "Heron"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Musket@test.com", "name": "Musket", "sub": "115804770028255050984", "squad": "Horse"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Net@test.com", "name": "Net", "sub": "115804770028255050984", "squad": "KillerWhale"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Nunchucks@test.com", "name": "Nunchucks", "sub": "115804770028255050984", "squad": "Kingfisher"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Pike@test.com", "name": "Pike", "sub": "115804770028255050984", "squad": "Lizard"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Pistol@test.com", "name": "Pistol", "sub": "115804770028255050984", "squad": "Moose"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Quarterstaff@test.com", "name": "Quarterstaff", "sub": "115804770028255050984", "squad": "Mouse"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Rapier@test.com", "name": "Rapier", "sub": "115804770028255050984", "squad": "Otter"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Rifle@test.com", "name": "Rifle", "sub": "115804770028255050984", "squad": "Owl"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Scimitar@test.com", "name": "Scimitar", "sub": "115804770028255050984", "squad": "Raccoon"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Shortbow@test.com", "name": "Shortbow", "sub": "115804770028255050984", "squad": "Raven"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Shortsword@test.com", "name": "Shortsword", "sub": "115804770028255050984", "squad": "Porcupine"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Shotgun@test.com", "name": "Shotgun", "sub": "115804770028255050984", "squad": "Salmon"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Sickle@test.com", "name": "Sickle", "sub": "115804770028255050984", "squad": "Seal"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Sling@test.com", "name": "Sling", "sub": "115804770028255050984", "squad": "Shark"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Spear@test.com", "name": "Spear", "sub": "115804770028255050984", "squad": "Snake"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Tank@test.com", "name": "Tank", "sub": "115804770028255050984", "squad": "Spider"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Torpedo@test.com", "name": "Torpedo", "sub": "115804770028255050984", "squad": "Squirrel"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Trident@test.com", "name": "Trident", "sub": "115804770028255050984", "squad": "Turtle"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "War pick@test.com", "name": "Warpick", "sub": "115804770028255050984", "squad": "Weasel"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Warhammer@test.com", "name": "Warhammer", "sub": "115804770028255050984", "squad": "Whale"},
              {"uuid": "tbd", "pictureBytes": "https://tbd", "email": "Whip@test.com", "name": "Whip", "sub": "115804770028255050984", "squad": "Wolf"}            
            ], 
        'squads': [
            {'name': 'kengraf57', 'score': 0},
              {"name": "Battleaxe"},
              {"name": "Blowgun"},
              {"name": "Chainsaw"},
              {"name": "Club"},
              {"name": "Crossbowhand"},
              {"name": "Crossbowheavy"},
              {"name": "Crossbowlight"},
              {"name": "Dagger"},
              {"name": "Dart"},
              {"name": "Drone"},
              {"name": "Flail"},
              {"name": "Flamethrower"},
              {"name": "Glaive"},
              {"name": "Greataxe"},
              {"name": "Greatclub"},
              {"name": "Greatsword"},
              {"name": "Grenade"},
              {"name": "Halberd"},
              {"name": "Handaxe"},
              {"name": "Javelin"},
              {"name": "Knife"},
              {"name": "Lance"},
              {"name": "Lighthammer"},
              {"name": "Longbow"},
              {"name": "Longsword"},
              {"name": "Mace"},
              {"name": "MachineGun"},
              {"name": "Maul"},
              {"name": "Morningstar"},
              {"name": "Musket"},
              {"name": "Net"},
              {"name": "Nunchucks"},
              {"name": "Pike"},
              {"name": "Pistol"},
              {"name": "Quarterstaff"},
              {"name": "Rapier"},
              {"name": "Rifle"},
              {"name": "Scimitar"},
              {"name": "Shortbow"},
              {"name": "Shortsword"},
              {"name": "Shotgun"},
              {"name": "Sickle"},
              {"name": "Sling"},
              {"name": "Spear"},
              {"name": "Tank"},
              {"name": "Torpedo"},
              {"name": "Trident"},
              {"name": "War pick"},
              {"name": "Warhammer"},
              {"name": "Whip"}
            ], 
        'machines': [
            {'name': 'nadialin', 'templateName': 'nadialin-base-template', 
             'services': [
                {'name': 'get_flag', 'protocol': 'http', 'expected_return': '{squad}', 'port': 49855, 'url': 'http://{ip}:49855/flag.txt', 'points': 10}, 
                  {"name": "Battleaxe", "protocol": "ssm", "expected_return": "Battleaxe", "url": "Battleaxe@{ip}", "points": 1},
                  {"name": "Blowgun", "protocol": "ssm", "expected_return": "Blowgun", "url": "Blowgun@{ip}", "points": 1},
                  {"name": "Chainsaw", "protocol": "ssm", "expected_return": "Chainsaw", "url": "Chainsaw@{ip}", "points": 1},
                  {"name": "Club", "protocol": "ssm", "expected_return": "Club", "url": "Club@{ip}", "points": 1},
                  {"name": "Crossbowhand", "protocol": "ssm", "expected_return": "Crossbowhand", "url": "Crossbowhand@{ip}", "points": 1},
                  {"name": "Crossbowheavy", "protocol": "ssm", "expected_return": "Crossbowheavy", "url": "Crossbowheavy@{ip}", "points": 1},
                  {"name": "Crossbowlight", "protocol": "ssm", "expected_return": "Crossbowlight", "url": "Crossbowlight@{ip}", "points": 1},
                  {"name": "Dagger", "protocol": "ssm", "expected_return": "Dagger", "url": "Dagger@{ip}", "points": 1},
                  {"name": "Dart", "protocol": "ssm", "expected_return": "Dart", "url": "Dart@{ip}", "points": 1},
                  {"name": "Drone", "protocol": "ssm", "expected_return": "Drone", "url": "Drone@{ip}", "points": 1},
                  {"name": "Flail", "protocol": "ssm", "expected_return": "Flail", "url": "Flail@{ip}", "points": 1},
                  {"name": "Flamethrower", "protocol": "ssm", "expected_return": "Flamethrower", "url": "Flamethrower@{ip}", "points": 1},
                  {"name": "Glaive", "protocol": "ssm", "expected_return": "Glaive", "url": "Glaive@{ip}", "points": 1},
                  {"name": "Greataxe", "protocol": "ssm", "expected_return": "Greataxe", "url": "Greataxe@{ip}", "points": 1},
                  {"name": "Greatclub", "protocol": "ssm", "expected_return": "Greatclub", "url": "Greatclub@{ip}", "points": 1},
                  {"name": "Greatsword", "protocol": "ssm", "expected_return": "Greatsword", "url": "Greatsword@{ip}", "points": 1},
                  {"name": "Grenade", "protocol": "ssm", "expected_return": "Grenade", "url": "Grenade@{ip}", "points": 1},
                  {"name": "Halberd", "protocol": "ssm", "expected_return": "Halberd", "url": "Halberd@{ip}", "points": 1},
                  {"name": "Handaxe", "protocol": "ssm", "expected_return": "Handaxe", "url": "Handaxe@{ip}", "points": 1},
                  {"name": "Javelin", "protocol": "ssm", "expected_return": "Javelin", "url": "Javelin@{ip}", "points": 1},
                  {"name": "Knife", "protocol": "ssm", "expected_return": "Knife", "url": "Knife@{ip}", "points": 1},
                  {"name": "Lance", "protocol": "ssm", "expected_return": "Lance", "url": "Lance@{ip}", "points": 1},
                  {"name": "Lighthammer", "protocol": "ssm", "expected_return": "Lighthammer", "url": "Lighthammer@{ip}", "points": 1},
                  {"name": "Longbow", "protocol": "ssm", "expected_return": "Longbow", "url": "Longbow@{ip}", "points": 1},
                  {"name": "Longsword", "protocol": "ssm", "expected_return": "Longsword", "url": "Longsword@{ip}", "points": 1},
                  {"name": "Mace", "protocol": "ssm", "expected_return": "Mace", "url": "Mace@{ip}", "points": 1},
                  {"name": "MachineGun", "protocol": "ssm", "expected_return": "MachineGun", "url": "MachineGun@{ip}", "points": 1},
                  {"name": "Maul", "protocol": "ssm", "expected_return": "Maul", "url": "Maul@{ip}", "points": 1},
                  {"name": "Morningstar", "protocol": "ssm", "expected_return": "Morningstar", "url": "Morningstar@{ip}", "points": 1},
                  {"name": "Musket", "protocol": "ssm", "expected_return": "Musket", "url": "Musket@{ip}", "points": 1},
                  {"name": "Net", "protocol": "ssm", "expected_return": "Net", "url": "Net@{ip}", "points": 1},
                  {"name": "Nunchucks", "protocol": "ssm", "expected_return": "Nunchucks", "url": "Nunchucks@{ip}", "points": 1},
                  {"name": "Pike", "protocol": "ssm", "expected_return": "Pike", "url": "Pike@{ip}", "points": 1},
                  {"name": "Pistol", "protocol": "ssm", "expected_return": "Pistol", "url": "Pistol@{ip}", "points": 1},
                  {"name": "Quarterstaff", "protocol": "ssm", "expected_return": "Quarterstaff", "url": "Quarterstaff@{ip}", "points": 1},
                  {"name": "Rapier", "protocol": "ssm", "expected_return": "Rapier", "url": "Rapier@{ip}", "points": 1},
                  {"name": "Rifle", "protocol": "ssm", "expected_return": "Rifle", "url": "Rifle@{ip}", "points": 1},
                  {"name": "Scimitar", "protocol": "ssm", "expected_return": "Scimitar", "url": "Scimitar@{ip}", "points": 1},
                  {"name": "Shortbow", "protocol": "ssm", "expected_return": "Shortbow", "url": "Shortbow@{ip}", "points": 1},
                  {"name": "Shortsword", "protocol": "ssm", "expected_return": "Shortsword", "url": "Shortsword@{ip}", "points": 1},
                  {"name": "Shotgun", "protocol": "ssm", "expected_return": "Shotgun", "url": "Shotgun@{ip}", "points": 1},
                  {"name": "Sickle", "protocol": "ssm", "expected_return": "Sickle", "url": "Sickle@{ip}", "points": 1},
                  {"name": "Sling", "protocol": "ssm", "expected_return": "Sling", "url": "Sling@{ip}", "points": 1},
                  {"name": "Spear", "protocol": "ssm", "expected_return": "Spear", "url": "Spear@{ip}", "points": 1},
                  {"name": "Tank", "protocol": "ssm", "expected_return": "Tank", "url": "Tank@{ip}", "points": 1},
                  {"name": "Torpedo", "protocol": "ssm", "expected_return": "Torpedo", "url": "Torpedo@{ip}", "points": 1},
                  {"name": "Trident", "protocol": "ssm", "expected_return": "Trident", "url": "Trident@{ip}", "points": 1},
                  {"name": "Warpick", "protocol": "ssm", "expected_return": "War pick", "url": "War pick@{ip}", "points": 1},
                  {"name": "Warhammer", "protocol": "ssm", "expected_return": "Warhammer", "url": "Warhammer@{ip}", "points": 1},
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

