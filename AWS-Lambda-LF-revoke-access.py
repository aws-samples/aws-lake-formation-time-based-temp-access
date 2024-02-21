import boto3
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def revoke_lake_formation_permissions(principal, database_name, table_name, permissions):
    """
    Revokes permissions for a principal on a specified Lake Formation resource.

    Parameters:
    - principal: A dictionary identifying the principal (e.g., IAM role or user) from whom to revoke permissions.
    - database_name: The name of the database containing the resource.
    - table_name: The name of the table resource.
    - permissions: A list of permissions to revoke.
    """
    lake_formation_client = boto3.client('lakeformation')
    resource = {
        'Table': {
            'DatabaseName': database_name,
            'Name': table_name,
            # 'CatalogId': 'ACCOUNT_ID'  # Uncomment and specify if necessary
        }
    }
    print(resource)
    try:
        response = lake_formation_client.revoke_permissions(
            Principal=principal,
            Resource=resource,
            Permissions=permissions,
            # PermissionsWithGrantOption=['ALL']  # Uncomment and specify if necessary
        )
        logger.info(f"Permissions revoked successfully: {response}")
        return {
            'statusCode': 200,
            'body': 'Access revoked successfully'
        }
    except Exception as e:
        logger.error(f"Error revoking AWS Lake Formation permissions: {e}")
        return {
            'statusCode': 500,
            'body': 'Failed to revoke access'
        }

def lambda_handler(event, context):
    """
    Handles the invocation of the Lake Formation permissions revocation.

    Expects event input from eventbridge
    with 
    principal- -expecting str 
    database name - expecting str
    table name-expecting str
    permissions- expecting a python list
    """
    # Extracting inputs from the event object passed by the eventbridge from LF-grant AWS Lambda
    in_principal = event.get('principal', {})
    principal = {'DataLakePrincipalIdentifier': in_principal}
    database_name = event.get('database_name', '')
    table_name = event.get('table_name', '')
    permissions = event.get('permissions', [])
    
  
    if not all([principal, database_name, table_name, permissions]):
        return {
            'statusCode': 400,
            'body': 'Missing required parameters'
        }

    return revoke_lake_formation_permissions(principal, database_name, table_name, permissions)

