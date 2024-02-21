import boto3
from datetime import datetime, timedelta
import json
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def grant_lake_formation_access(principal, permission, database_name, table_name):
    """
    Grants access to a Lake Formation resource.

    Returns True if access was successfully granted, False otherwise.
    """
    lake_formation_client = boto3.client('lakeformation')
     
    # Define the principal and resource to grant permissions to
    principal = {'DataLakePrincipalIdentifier': principal}
    resource = {
        'Table': {
            'DatabaseName': database_name,
            'Name': table_name,
        }
    }
    permissions = permission

    try:
        response = lake_formation_client.grant_permissions(
            Principal=principal,
            Resource=resource,
            Permissions=permissions,
        )
        logger.info(f"Access granted successfully: {response}")
        return True
    except Exception as e:
        logger.error(f"Error granting Lake Formation access: {e}")
        return False

def schedule_event_bridge(duration, revoke_lambda_arn, principal, permissions, database_name, table_name):
    """
    Schedules an EventBridge rule to trigger a Lambda function after a specified duration, passing necessary details for access revocation.

    Parameters:
    - duration: Duration in hours after which the EventBridge rule should trigger.
    - revoke_lambda_arn: ARN of the Lambda function to be triggered.
    - principal: Principal information for access revocation.
    - permissions: Permissions to be revoked.
    - database_name: Name of the Lake Formation database.
    - table_name: Name of the Lake Formation table.
    """
    revoke_time = datetime.utcnow() + timedelta(hours=duration)
    cron_expression = revoke_time.strftime('cron(%M %H %d %m ? %Y)')
    
    eventbridge = boto3.client('events')
    rule_name = 'RevokeAccessRule-' + revoke_time.strftime('%Y%m%d%H%M%S')
    
    try:
        eventbridge.put_rule(
            Name=rule_name,
            ScheduleExpression=cron_expression,
            State='ENABLED',
            Description=f'Rule to revoke AWS Lake formation access after {duration} hours'
        )
        
        revoke_details = {
            'principal': principal,
            'permissions': permissions,
            'database_name': database_name,
            'table_name': table_name,
        }
        
        eventbridge.put_targets(
            Rule=rule_name,
            Targets=[
                {
                    'Id': 'RevokeAccessLambdaFunction',
                    'Arn': revoke_lambda_arn,
                    'Input': json.dumps(revoke_details),
                }
            ]
        )
        logger.info(f"EventBridge rule scheduled successfully for {revoke_time.strftime('%Y-%m-%d %H:%M:%S UTC')} with revoke details.")
    except Exception as e:
        logger.error(f"Error scheduling EventBridge rule: {e}")

# Example use of schedule_event_bridge function
# schedule_event_bridge(24, 'arn:aws:lambda:REGION:ACCOUNT_ID:function:FUNCTION_NAME',
#                       {'DataLakePrincipalIdentifier': 'arn:aws:iam::ACCOUNT_ID:role/ROLE_NAME'},
#                       ['SELECT'], 'your_database', 'your_table')

def lambda_handler(event, context):
    """
    Grants Lake Formation access and schedules an EventBridge rule to revoke access after 24 hours.
    """
    
    revoke_lambda_arn = 'arn:aws:lambda:region:AccountN:function:revokeLFAccess'
    principal='arn:aws:iam::AccountN:role/<principle>'
    permission=['SELECT']
    database_name='<db_name>'
    table_name='<table_nm>'
    duration = 1
    
    
    grant_lake_formation_access(principal, permission, database_name, table_name)
    
    
    if grant_lake_formation_access(principal, permission, database_name, table_name):
        # Ensure to replace REGION, ACCOUNT_ID, and FUNCTION_NAME with actual values
        schedule_event_bridge(duration, revoke_lambda_arn, principal, permission, database_name, table_name)
    else:
        logger.error("Failed to grant Lake Formation access. EventBridge rule not scheduled.")
