import json
import boto3
from datetime import datetime

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = 'HotelBookingDetails'  # Replace with your DynamoDB table name
table = dynamodb.Table(table_name)

def validate(slots):

    if not slots['Location']:
        print("Inside Empty Location")
        return {
            'isValid': False,
            'violatedSlot': 'Location'
        } 
        
    if not slots['HotelNames']:
        return {
            'isValid': False,
            'violatedSlot': 'HotelNames',
        }        

    if not slots['CheckInDate']:
        return {
            'isValid': False,
            'violatedSlot': 'CheckInDate',
        }
    
    if not slots['Time']:
        return {
            'isValid': False,
            'violatedSlot': 'Time'
        }
    
    if not slots['Nights']:
        return {
            'isValid': False,
            'violatedSlot': 'Nights'
        }
    
    if not slots['RoomType']:
        return {
            'isValid': False,
            'violatedSlot': 'RoomType'
        }
    
    if not slots['PhoneNumber']:
        return {
            'isValid': False,
            'violatedSlot': 'PhoneNumber'
        }
    
    return {'isValid': True}

def extract_interpreted_value(slot):
    """Extract the interpreted value from the slot data."""
    if 'value' in slot and 'interpretedValue' in slot['value']:
        return slot['value']['interpretedValue']
    return None

def store_user_details(slots):
    # Extract interpreted values
    user_id = extract_interpreted_value(slots.get('PhoneNumber', {}))
    name = extract_interpreted_value(slots.get('Name', {}))
    location = extract_interpreted_value(slots.get('Location', {}))
    hotel_names = extract_interpreted_value(slots.get('HotelNames', {}))
    check_in_date = extract_interpreted_value(slots.get('CheckInDate', {}))
    time = extract_interpreted_value(slots.get('Time', {}))
    nights = extract_interpreted_value(slots.get('Nights', {}))
    room_type = extract_interpreted_value(slots.get('RoomType', {}))

    # Ensure values are strings or empty if None
    table.put_item(
        Item={
            'UserId': user_id if user_id else "Unknown",  # Use a default value if None
            'Name' : name if name else "Unknown",
            'Location': location if location else "Unknown",
            'HotelNames': hotel_names if hotel_names else "Unknown",
            'CheckInDate': check_in_date if check_in_date else "Unknown",
            'Time': time if time else "Unknown",
            'Nights': nights if nights else "Unknown",
            'RoomType': room_type if room_type else "Unknown",
            'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    )


def lambda_handler(event, context):
    
    slots = event['sessionState']['intent']['slots']
    intent = event['sessionState']['intent']['name']
    print(event['invocationSource'])
    print(slots)
    print(intent)
    validation_result = validate(slots)
    
    if event['invocationSource'] == 'DialogCodeHook':
        if not validation_result['isValid']:
            response = {
                "sessionState": {
                    "dialogAction": {
                        'slotToElicit': validation_result['violatedSlot'],
                        "type": "ElicitSlot"
                    },
                    "intent": {
                        'name': intent,
                        'slots': slots
                    }
                }
            }
        else:
            # Store user details in DynamoDB if validation is successful
            store_user_details(slots)
            
            response = {
                "sessionState": {
                    "dialogAction": {
                        "type": "Delegate"
                    },
                    "intent": {
                        'name': intent,
                        'slots': slots
                    }
                }
            }
        return response
