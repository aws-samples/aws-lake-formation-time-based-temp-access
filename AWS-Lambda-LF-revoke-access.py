import boto3
import uuid
import time
import logging
import json

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS SDK clients
dynamodb = boto3.resource('dynamodb')
lakeformation = boto3.client('lakeformation')

def grant_access_to_lakeformation(principal, resource, permissions):
    """
    Grants access to a Lake Formation resource.
    """
    try:
        response = lakeformation.grant_permissions(
            Principal={'DataLakePrincipalIdentifier': principal},
            Resource=resource,
            Permissions=permissions,
        )
        logger.info("Lake Formation permission granted: %s", response)
        return True
    except Exception as e:
        logger.error("Error granting Lake Formation permission: %s", e, exc_info=True)
        return False

def log_access_grant_to_dynamodb(access_id, principal, resource_info, duration_hours):
    """
    Logs the access grant details to a DynamoDB table.
    """
    table_name = 'LakeFormationAccessGrants'
    current_timestamp = int(time.time())
    
    try:
        table = dynamodb.Table(table_name)
        response = table.put_item(
            Item={
                'AccessID': access_id,
                'PrincipalID': principal,
                'ResourceInfo': json.dumps(resource_info),  # Ensure this is a valid JSON string
                'GrantTimestamp': current_timestamp,
                'DurationHours': duration_hours,
                'IsActive': True  # Mark the grant as active initially
            }
        )
        logger.info("Access grant logged to DynamoDB: %s", response)
    except Exception as e:
        logger.error("Error logging access grant to DynamoDB: %s", e, exc_info=True)

def update_access_grant_status_in_dynamodb(access_id, is_active):
    """
    Updates the active status of an access grant in DynamoDB.
    """
    table_name = 'LakeFormationAccessGrants'
    table = dynamodb.Table(table_name)
    
    try:
        response = table.update_item(
            Key={'AccessID': access_id},
            UpdateExpression="set IsActive = :val",
            ExpressionAttributeValues={':val': is_active}
        )
        logger.info(f"Access grant status updated in DynamoDB for {access_id}: {response}")
    except Exception as e:
        logger.error(f"Error updating access grant status in DynamoDB for {access_id}: {e}", exc_info=True)

def check_and_revoke_access():
    """
    Checks for access grants that have expired and revokes them.
    """
    table = dynamodb.Table('LakeFormationAccessGrants')
    current_time = int(time.time())
    
    response = table.scan()
    
    found_eligible_for_revocation = False
    
    for item in response['Items']:
        grant_time = item['GrantTimestamp']
        duration_hours = item['DurationHours']
        
        if current_time - grant_time > duration_hours * 3600 and item['IsActive']:
            found_eligible_for_revocation = True
            principal = item['PrincipalID']
            resource_info = json.loads(item['ResourceInfo'])
            
            if revoke_access_in_lakeformation(principal, resource_info):
                update_access_grant_status_in_dynamodb(item['AccessID'], False)
    
    if not found_eligible_for_revocation:
        logger.info("No eligible access revoke records found in DynamoDB table.")

def revoke_access_in_lakeformation(principal, resource_info):
    """
    Revokes access to a Lake Formation resource for a given principal.
    """
    # Assuming resource_info is already in the correct format for the Lake Formation API call
    try:
        lakeformation.revoke_permissions(
            Principal={'DataLakePrincipalIdentifier': principal},
            Resource=resource_info,
            Permissions=['SELECT'],  # Adjust as needed
        )
        logger.info(f"Successfully revoked Lake Formation permissions for {principal}")
        return True
    except Exception as e:
        logger.error(f"Error revoking Lake Formation permissions for {principal}: {e}", exc_info=True)
        return False



def lambda_handler(event, context):
    check_and_revoke_access()
    return {
        'statusCode': 200,
        'body': 'Access revocation process completed.'
    }
