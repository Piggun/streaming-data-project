# Streaming Data Project
## Overview
This application's purpose is to retrieve articles from [The Guardian API](https://open-platform.theguardian.com/) and publish them to a message broker ([AWS SQS](https://aws.amazon.com/sqs/) in this case)
so that they can be consumed and analysed by other applications.
## Prerequisites
You will need:
- An AWS account ([here](https://aws.amazon.com/free/?trk=ce1f55b8-6da8-4aa2-af36-3f11e9a449ae&sc_channel=ps&ef_id=CjwKCAjw0aS3BhA3EiwAKaD2Zd4eSzqJyvnPssM2UByAVeg_mrGNPxuC6PxNBQSVbrT5euOhsaoMGBoCat4QAvD_BwE:G:s&s_kwcid=AL!4422!3!433803620870!e!!g!!aws%20account!9762827897!98496538463&gbraid=0AAAAADjHtp8btQnqCl1DlNkqa2lS_phD1&gclid=CjwKCAjw0aS3BhA3EiwAKaD2Zd4eSzqJyvnPssM2UByAVeg_mrGNPxuC6PxNBQSVbrT5euOhsaoMGBoCat4QAvD_BwE&all-free-tier.sort-by=item.additionalFields.SortRank&all-free-tier.sort-order=asc&awsf.Free%20Tier%20Types=*all&awsf.Free%20Tier%20Categories=*all))
- To create an AWS Queue (instructions [here](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/creating-sqs-standard-queues.html))
- To get an API Key for The Guardian API ([here](https://open-platform.theguardian.com/access/))

**Optionally** you will need to create an Amazon DynamoDB table (instructions [here](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/getting-started-step-1.html)) in case you want to be able to track the API usage and limit its requests available per day.
&rarr; ***This is optional and it is <ins>NOT</ins> required, the application will work regardless.***
## Local Setup
Use the following instructions to correctly set up the environment in order to use the application.
1. Run `git clone https://github.com/Piggun/streaming-data-project.git` in your terminal, to clone the repo at your desired location
2. Run `cd streaming-data-project` to move inside the repo's root folder
3. Run `make create-environment` to create a virtual environment in which to install dependencies
4. Run `source venv/bin/activate` to activate the created environment
5. Run `make install-dependencies` to install the dependencies required by the application to be able to run

Once you have run the above commands you will have to:
1. Create a new `.env` file
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
     - Click on your queue
     - Select 'Send and recieve messages'
     - And click 'Poll for messages'
- **From the terminal**:
     - Run `aws sqs receive-message --queue-url [Your-Queue-URL-here] --max-number-of-messages 10`
     - More informations can be found [here](https://docs.aws.amazon.com/cli/latest/reference/sqs/receive-message.html)

## Makefile commands
- `make run-unit-tests` : Runs unit-tests, checking that every function behaves correctly
- `make run-security-checks` : Scans for security issues
- `make run-black` : Formats code
- `make run-flake8` : Checks if the code is PEP-8 compliant
- `make zip-lambda` : Zips the app along with its dependencies, useful if you want to upload the function to AWS Lambda
- `make create-environment` : Creates a virtual environment
- `make install-dependencies` : Install all the dependencies listed in requirements.txt
