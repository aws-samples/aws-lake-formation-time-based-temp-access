<h1><p><u>AWS-Lake-Formation-Time-based-Temp-Access</u></p></h1>

### Introduction
This aws-samples repository contains a workflow that automates time-based access control for AWS Lake Formation resources using AWS Lambda and Amazon EventBridge. This solution grants temporary access to AWS Lake Formation tables and automatically revokes it after a specified duration, enhancing security and compliance by ensuring that access is only available when necessary.

### Workflow Architecture
This architecture leverages AWS Lambda and Amazon EventBridge to provide a secure, automated mechanism for granting and revoking access to AWS Lake Formation resources based on predefined durations. The system operates in two main phases: access grant and access revocation, facilitated by two distinct Lambda functions.

**Phase 1: Access Grant**
Trigger: The process begins when a user provides input, specifying the principal (e.g., an AWS IAM role or user) and the duration for which access is required.
Lambda Function (Grant Access): A AWS Lambda function (AccessGrant) is invoked with the user's input. This function performs the following tasks:

**Grant Access:** It grants the specified principal access to the desired AWS Lake Formation resources using AWS Lake Formation's GrantPermissions API.

**Schedule Revocation:** It then creates a scheduled event in Amazon EventBridge, set to trigger after the specified duration. This scheduling is achieved by dynamically setting the cron expression based on the duration for which access was granted.

**Phase 2: Access Revocation**

**Scheduled Event:** Upon reaching the specified duration, Amazon EventBridge triggers a second Lambda function (RevokeAccess) according to the schedule set during the access grant phase.
Lambda Function (Revoke Access): The RevokeAccess function is invoked by Amazon EventBridge at the scheduled time. This function performs the following task:

**Revoke Access:** It revokes the previously granted access from the principal, ensuring that the temporary access permission is securely and automatically removed.


![Architecture](https://github.com/aws-samples/aws-lake-formation-time-based-temp-access/blob/main/Architecture.jpg)
***

### Why Is It Useful?
In environments where data security and compliance are paramount, limiting access duration to sensitive data can significantly reduce risk. This workflow automates the process of granting and revoking access, eliminating human error and ensuring that permissions are only available for the time they are needed. It's particularly useful for scenarios involving temporary workers, short-term projects, or time-bound data analysis tasks.

### Example Use Case
A data analytics firm needs to grant a contractor temporary access to a specific dataset stored in AWS Lake Formation for a period of 48 hours. Using this workflow, the firm can automate the process, ensuring the contractor only has access for the specified time, after which access is automatically revoked, thus maintaining data security and compliance.

### Prerequisites
Before you can use this workflow, you need to have the following:

* An AWS account with permissions to manage AWS Lambda, AWS Lake Formation, and Amazon EventBridge.
* The AWS CLI installed and configured.
* Python 3.8 or higher.
* Basic familiarity with AWS services, particularly AWS Lambda, AWS Lake Formation, and Amazon EventBridge.
* Ensure the AWS Lambda for revokeLFAccess has Resource-based policy(under permission) statements has event.amazonaws.com and lambda:InvokeFunction

### Getting Started
Setting Up Your Environment
Clone the repository:

Copy code
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
        }
    ]
}

```

#### SAM Template-Automated Deployment 

To streamline the AWS SAM (Serverless Application Model) template for deploying two AWS Lambda functions with specific roles and permissions for managing AWS Lake Formation access, along with the necessary permissions for AWSEventBridge to invoke one of the AWS Lambda functions, here's a concise explanation followed by a two-step execution guide:

#### Template Overview
This SAM template defines:

A LambdaExecutionRole with policies for AWS Lake Formation access management and AWS CloudWatch Logs creation, alongside permissions to manage EventBridge rules.

* Two Lambda functions:
LambdaRevokeAccess: Revokes Lake Formation access.
LambdaAccessGrant: Grants Lake Formation access and is configured with an Amazon EventBridge rule trigger.
LambdaInvokePermissionForEventBridge: Grants EventBridge permission to invoke the LambdaAccessGrant function.

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
