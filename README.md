# Streaming Data Project
## Overview
This application's purpose is to retrieve articles from [The Guardian API](https://open-platform.theguardian.com/) and publish them to a message broker ([AWS SQS](https://aws.amazon.com/sqs/) in this case)
so that they can be consumed and analysed by other applications.\
The application accepts a search term (e.g. "science"), a reference to the message broker, and an optional "date_from" field. It uses the search terms to search for articles in The Guardian API and then posts details of up to ten hits to the message broker.
## Prerequisites
You will need:
- An AWS account ([here](https://aws.amazon.com/free/?trk=ce1f55b8-6da8-4aa2-af36-3f11e9a449ae&sc_channel=ps&ef_id=CjwKCAjw0aS3BhA3EiwAKaD2Zd4eSzqJyvnPssM2UByAVeg_mrGNPxuC6PxNBQSVbrT5euOhsaoMGBoCat4QAvD_BwE:G:s&s_kwcid=AL!4422!3!433803620870!e!!g!!aws%20account!9762827897!98496538463&gbraid=0AAAAADjHtp8btQnqCl1DlNkqa2lS_phD1&gclid=CjwKCAjw0aS3BhA3EiwAKaD2Zd4eSzqJyvnPssM2UByAVeg_mrGNPxuC6PxNBQSVbrT5euOhsaoMGBoCat4QAvD_BwE&all-free-tier.sort-by=item.additionalFields.SortRank&all-free-tier.sort-order=asc&awsf.Free%20Tier%20Types=*all&awsf.Free%20Tier%20Categories=*all))
- To create an AWS Queue (instructions [here](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/creating-sqs-standard-queues.html))
- To get an API Key for The Guardian API ([here](https://open-platform.theguardian.com/access/))

**Optionally** you can create an Amazon DynamoDB table (instructions [here](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/getting-started-step-1.html)) in case you want to be able to track the API usage and limit its requests available per day.
&rarr; ***This is optional and it is <ins>NOT</ins> required, the application will work regardless.***

**Alternatively** you can easily create an AWS Queue and DynamoDB using Terraform:

*Please bear in mind that you will first need to go through the [AWS Setup](#aws-setup) before running Terraform.*
1. Install Terraform (instructions [here](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli))
2. Run `cd terraform` to move into Terraform's folder
3. Run `terraform init` to initialise Terraform
4. Run `terraform apply` to build the plan
5. Enter `yes` when prompted and press Enter
## Local Setup
Use the following instructions to correctly set up the environment in order to use the application.
1. Run `git clone https://github.com/Piggun/streaming-data-project.git` in your terminal, to clone the repo at your desired location
2. Run `cd streaming-data-project` to move inside the repo's root folder
3. Run `make create-environment` to create a virtual environment in which to install dependencies
4. Run `source venv/bin/activate` to activate the created environment
5. Run `make install-dependencies` to install the dependencies required for the application to run

Once you have run the above commands you will have to:
1. Create a new `.env` file in the root folder
2. Populate the `.env` file with your The Guardian API Key and your SQS Queue URL like so ( please replace the items in brackets [ ] ):

   ```
   API_KEY="[Your-The-Guardian-API-Key-here]"
   SQS_URL="[Your-SQS-Queue-URL-here]"
   ```

You have now completed the local setup and are now ready to proceed to the AWS configuration.

## AWS Setup
1. Create an IAM user (instructions [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html#id_users_create_console))
2. Attach the following policies to the user (instructions [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_manage-attach-detach.html)) &rarr; AmazonSQSFullAccess, AmazonDynamoDBFullAccess, AWSLambda_FullAccess
3. Create an AWS Access Key (instructions [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey))
4. Install the AWS CLI (instructions [here](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html#getting-started-install-instructions))
6. Configure the AWS CLI (instructions [here](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/configure/index.html)) by providing your AWS Access Key, your Secret Access Key and your region name

You have now completed all the setups and should now be ready to run the application.

## Running the program
While inside the project's root folder, run the following command in the terminal, replacing the items in brackets [ ] with meaningful content:
```
python app.py --search_term "[Your search term]" --reference "[Your content]" --date_from "[2024-02-27]"
```
E.g.
```
python app.py --search_term "science" --reference "science_content" --date_from "2024-08-16" 
```
**Input options:**


`--search_term` (REQUIRED) : The search term used to look for articles

`--reference` (REQUIRED) : The reference label that will be attached to each message sent to SQS

`--date_from` (OPTIONAL) : Used to look for articles published on or after the specified date

## Visualising your data
To visualize the data:
- **From the AWS Management Console** :
     - Go to AWS SQS
     - Click on your queue ('the-guardian-articles' if created with the provided Terraform plan)
     - Select 'Send and receive messages'
     - And click 'Poll for messages'
- **From the terminal**:
     - Run `aws sqs receive-message --queue-url [Your-Queue-URL-here] --max-number-of-messages 10`
     - More information can be found [here](https://docs.aws.amazon.com/cli/latest/reference/sqs/receive-message.html)

To track the API usage:
- **From the AWS Management Console** :
     - Go to AWS DynamoDB
     - Click on 'tables'
     - Select your table ('request-counter' if created with the provided Terraform plan)
     - And click on 'Explore table items'
- **From the terminal**:
     - Run  `aws dynamodb get-item  --table-name [Your-table-name-here] --key '{"Date": {"S": "[The-date-to-track]"}}'`

       E.g. `aws dynamodb get-item  --table-name request-counter --key '{"Date": {"S": "2024-09-23"}}'`
     - More information can be found [here](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/getting-started-step-3.html)


## Makefile commands
- `make run-unit-tests` : Runs unit-tests, checking that every function behaves correctly
- `make run-security-checks` : Scans for security issues
- `make run-black` : Formats code
- `make run-flake8` : Checks if the code is PEP-8 compliant
- `make zip-lambda` : Zips the app along with its dependencies, useful if you want to upload the function to AWS Lambda
- `make create-environment` : Creates a virtual environment
- `make install-dependencies` : Install all the dependencies listed in requirements.txt
