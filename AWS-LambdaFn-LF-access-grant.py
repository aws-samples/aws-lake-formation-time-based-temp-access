import boto3
import uuid,json
import time
import logging

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS SDK clients
dynamodb_client = boto3.client('dynamodb')
lakeformation_client = boto3.client('lakeformation')

def grant_access_to_lakeformation(principal, resource, permissions):
    """
    Grants access to a Lake Formation resource.

    :param principal: The ARN of the IAM user or role to grant permissions to.
    :param resource: A dictionary defining the Lake Formation resource.
    :param permissions: A list of permissions to grant.
    """
    try:
        response = lakeformation_client.grant_permissions(
            Principal={'DataLakePrincipalIdentifier': principal},
            Resource=resource,
            Permissions=permissions,
            # PermissionsWithGrantOption may be included if needed
        )
        logger.info("Lake Formation permission granted: %s", response)
        return {'success': True, 'message': 'Lake Formation permission granted.', 'response': response}
    except Exception as e:
        logger.error("Error granting Lake Formation permission: %s", e)
        return {'success': False, 'message': f'Error granting Lake Formation permission: {e}'}

def log_access_grant_to_dynamodb(access_id, principal, resource_info, duration_hours):
    """
    Logs the access grant details to a DynamoDB table.

    :param access_id: Unique identifier for the access grant.
    :param principal: The ARN of the principal that was granted access.
    :param resource_info: JSON string of the Lake Formation resource.
    :param duration_hours: The duration in hours for which access was granted.
    """
    table_name = 'LakeFormationAccessGrants'  # Ensure this matches your DynamoDB table name
    current_timestamp = int(time.time())
    
    try:
        response = dynamodb_client.put_item(
            TableName=table_name,
            Item={
                'AccessID': {'S': access_id},
                'PrincipalID': {'S': principal},
                'ResourceInfo': {'S': resource_info},
                'GrantTimestamp': {'N': str(current_timestamp)},
                'DurationHours': {'N': str(duration_hours)},
                'IsActive': {'BOOL': True}  # Mark the grant as active initially
            }
        )
        logger.info("Access grant logged to DynamoDB: %s", response)
        return {'success': True, 'message': 'Access grant logged to DynamoDB.', 'response': response}
    except Exception as e:
        logger.error("Error logging access grant to DynamoDB: %s", e)
        return {'success': False, 'message': f'Error logging access grant to DynamoDB: {e}'}

def lambda_handler(event, context):
    # Example values for demonstration purposes
    
    principal='<principle>'
    permission=['SELECT']
    database_name='<DB_name>'
    table_name='<table_nm>'
    duration = 1 # in hours

    
    # Extract duration from the event, defaulting to 24 hours if not specified
    duration_hours = event.get(duration, 24)
    
    resource = {
        'Table': {
            'DatabaseName': database_name,
            'Name': table_name
        }
    }
    
    # Generate a unique AccessID
    access_id = str(uuid.uuid4())
    
    # Convert the resource definition to a string for logging purposes
    resource_info = json.dumps(resource)
    
    grant_result = grant_access_to_lakeformation(principal, resource, permission)
    
    if grant_result['success']:
        log_result = log_access_grant_to_dynamodb(access_id, principal, resource_info, duration_hours)
        if log_result['success']:
            logger.info("Successfully granted access and logged to DynamoDB.")
            return {'success': True, 'message': 'Access granted and logged.'}
        else:
            logger.error("Failed to log access grant to DynamoDB.")
            return {'success': False, 'message': log_result['message']}
    else:
        logger.error("Failed to grant Lake Formation access.")
        return {'success': False, 'message': grant_result['message']}
