<h1><p><u>AWS-Lake-Formation-Time-based-Temp-Access</u></p></h1>

### Introduction:
The architecture diagram presents a workflow for managing time-based temporary access to AWS Lake Formation (LF) resources using AWS Lambda and Amazon DynamoDB, with the scheduling capabilities of Amazon EventBridge. This automated solution is designed to grant temporary access permissions and ensure that they are revoked after a specified duration, enhancing security and adherence to the principle of least privilege.


### Workflow Architecture
**API Gateway (Optional)**: Serves as an entry point for initiating the workflow. It can expose an HTTP endpoint for users or services to request temporary access to Lake Formation resources.

**AWS Lambda (Grant Access)**: This Lambda function is triggered by the API Gateway to grant temporary access to Lake Formation resources. It uses the AWS SDK (boto3) to interact with AWS Lake Formation.

**Amazon DynamoDB**: Stores records of all granted accesses, including details like the principal, resource, and access duration.

**AWS Lambda (Scan & Revoke Access)**: Periodically triggered by EventBridge, this function scans the DynamoDB table for access records that have expired and revokes those accesses.

**Amazon EventBridge:** Schedules and triggers the Scan & Revoke Lambda function based on the duration specified in the access grant records.


**Phase 1: Access Grant**
1. **Grant Access**:
* A user or service makes a request for temporary access to a AWS Lake Formation resource, optionally via an AWS API Gateway endpoint.
The request triggers the Grant Access AWS Lambda function, which validates the request and uses boto3 to call AWS Lake Formation's GrantPermissions API, granting the specified permissions.
The AWS Lambda function logs the access grant details, including the duration of access, in a DynamoDB table, and marks the grant as active.

2. **Log Access Grants**:

* The details of the access grant, such as principal ID, resource information, and duration, are stored in a Amazon DynamoDB table with a unique access ID and a timestamp.
An IsActive attribute is set to True, indicating that the grant is currently in effect.

3. **Scheduled Revocation Check**:

* Amazon EventBridge is configured with a rule to trigger the Scan & Revoke AWS Lambda function at regular intervals.
Upon invocation, the AWS Lambda function scans the Amazon DynamoDB table for records where the current time exceeds the grant timestamp plus the duration, indicating that the access period has expired.

4. **Revoke Access:**
For each expired grant, the Scan & Revoke Lambda function calls AWS Lake Formation's RevokePermissions API to revoke the access.
The function updates the Amazon DynamoDB table, setting the IsActive attribute to False for the revoked grant to reflect that the access is no longer active.

**Completion:**
After processing, the Scan & Revoke AWS Lambda function concludes its execution, and the system awaits the next scheduled Amazon EventBridge trigger to repeat the process if necessary.
Optionally, if any steps fail or exceptions occur, appropriate error logging is provided for monitoring and alerting purposes.
This architecture ensures that temporary access to sensitive data is automatically managed and that permissions are revoked in a timely manner, reducing the risk of unauthorized access and maintaining a robust security posture.


![Architecture](https://github.com/aws-samples/aws-lake-formation-time-based-temp-access/blob/main/Architecture.jpg)
***

### Why Is It Useful?
In environments where data security and compliance are paramount, limiting access duration to sensitive data can significantly reduce risk. This workflow automates the process of granting and revoking access, eliminating human error and ensuring that permissions are only available for the time they are needed. It's particularly useful for scenarios involving temporary workers, short-term projects, or time-bound data analysis tasks.

### Example Use Case
A data analytics firm needs to grant a contractor temporary access to a specific dataset stored in AWS Lake Formation for a period of 48 hours. Using this workflow, the firm can automate the process, ensuring the contractor only has access for the specified time, after which access is automatically revoked, thus maintaining data security and compliance.

### Prerequisites
Before you can use this workflow, you need to have the following:

* An AWS account with permissions to manage AWS Lambda, AWS Lake Formation, Amazon DynamoDB and Amazon EventBridge.
* The AWS CLI installed and configured.
* Python 3.8 or higher.
* Basic familiarity with AWS services, particularly AWS Lambda, AWS Lake Formation,Amazon DynamoDB and Amazon EventBridge.
* Ensure the AWS Lambda for Scan and revoke has Resource-based policy(under permission) statements has event.amazonaws.com and lambda:InvokeFunction

### Getting Started
Setting Up Your Environment
Clone the repository:


```
git clone https://github.com/aws-samples/aws-lake-formation-time-based-temp-access.git
```
```
cd aws-lake-formation-time-based-temp-access
```


#### Configuring AWS Resources
* Create IAM roles for AWS Lambda functions with permissions to access AWS Lake Formation(add as a data admin) and AWS EventBridge. Ensure the AWS Lambda execution role is added as an admin to AWS Lake Formation.

* Set up Lake Formation: Ensure your data lake is configured, and you have tables created in AWS Lake Formation to test the access control.

* Deploy Lambda functions: Upload the Python scripts to AWS Lambda. 

#### Usage

### IAM Policy reccomendations
Best Practices and Standards
* **Principle of Least Privilege:** Always aim to grant the minimum permissions necessary for the tasks. Review and tighten IAM policies regularly.
* **Regular Audits:** Periodically audit AWS IAM roles and policies to ensure they remain aligned with current requirements and best practices.
* **Use Condition Keys:** Where possible, use condition keys in your AWS IAM policies to further restrict permissions based on specific conditions.
* **Secure Your AWS Lambda Environment**: Ensure your AWSLambda functions are running on the latest supported runtime and follow security best practices for code and dependencies.
* **Monitoring and Logging:** Enable CloudWatch Logs for your Lambda functions and configure monitoring to alert on unauthorized or unexpected actions.

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lakeformation:GetDataAccess",
                "lakeformation:GrantPermissions",
                "lakeformation:RevokePermissions",
                "lakeformation:ListPermissions",
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "events:PutRule",
                "events:PutTargets",
                "events:DeleteRule",
                "events:RemoveTargets",
                "events:DescribeRule",
                "events:ListTargetsByRule"
            ],
            "Resource": "arn:aws:events:<region>:<account-id>:rule/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:Scan",
                "dynamodb:UpdateItem",
                "dynamodb:PutItem"
                // Include other DynamoDB actions as needed by your Lambda function
            ],
            "Resource": [
                "arn:aws:dynamodb:<region>:<account-id>:table/tablename"
                // Replace with the ARN of the specific Amazon DynamoDB table(s) your Lambda will interact with
            ]
        }
    ]
}


```

#### AWS SAM Template-Automated Deployment 

The AWS SAM template is engineered to automate the provisioning of a secure access management system for AWS Lake Formation. It establishes a LambdaExecutionRole with the necessary permissions to manage AWS Lake Formation permissions, AWS CloudWatch Logs, and Amazon EventBridge rules. The template deploys two AWS Lambda functions: LambdaRevokeAccess for revoking access permissions, and LambdaAccessGrant for granting permissions, which is also equipped with an AWS API Gateway endpoint for invocation. It includes a Amazon DynamoDB table, LakeFormationAccessGrants, to log access details, and an AWS EventBridge rule, RevokeAccessSchedule, set to trigger the LambdaRevokeAccess function on an hourly basis. This configuration ensures an automated, scheduled check for permission revocation, maintaining tight security controls around data access.

#### Execution Steps

#### Deploy the SAM Template

* Git clone the repository and cd into the directory.

* Run the following commands to deploy your application:
```
sam build

sam deploy --guided
```
The sam build command compiles your application and prepares it for deployment. The sam deploy --guided command walks you through the deployment process, where you'll specify your AWS region, stack name, and any parameters required by the template.


### Contributing
Contributions are welcome! Please follow the guidelines in the CONTRIBUTING.md file for details on how to submit pull requests, report issues, or suggest enhancements.

### License
This project is licensed under the MIT License - see the LICENSE file for details.
