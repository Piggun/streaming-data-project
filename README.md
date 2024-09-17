# Streaming Data Project
## Overview
This application's purpose is to retrieve articles from the [Guardian API](https://open-platform.theguardian.com/) and publish them to a message broker ([AWS SQS](https://aws.amazon.com/sqs/) in this case)
so that they can be consumed and analysed by other applications.
## Prerequisites
You will need:
- An AWS account ([here](https://aws.amazon.com/free/?trk=ce1f55b8-6da8-4aa2-af36-3f11e9a449ae&sc_channel=ps&ef_id=CjwKCAjw0aS3BhA3EiwAKaD2Zd4eSzqJyvnPssM2UByAVeg_mrGNPxuC6PxNBQSVbrT5euOhsaoMGBoCat4QAvD_BwE:G:s&s_kwcid=AL!4422!3!433803620870!e!!g!!aws%20account!9762827897!98496538463&gbraid=0AAAAADjHtp8btQnqCl1DlNkqa2lS_phD1&gclid=CjwKCAjw0aS3BhA3EiwAKaD2Zd4eSzqJyvnPssM2UByAVeg_mrGNPxuC6PxNBQSVbrT5euOhsaoMGBoCat4QAvD_BwE&all-free-tier.sort-by=item.additionalFields.SortRank&all-free-tier.sort-order=asc&awsf.Free%20Tier%20Types=*all&awsf.Free%20Tier%20Categories=*all))
- To create an AWS Queue (instructions [here](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/creating-sqs-standard-queues.html))
- To get an API Key for The Guardian API ([here](https://open-platform.theguardian.com/access/))

**Optionally** you will need to create an Amazon DynamoDB table (instruction [here](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/getting-started-step-1.html)) in case you want to be able to track the API usage and limit its requests available per day.
&rarr; ***This is optional and it is <ins>NOT</ins> required, the application will work regardless.***
## Setup
Use the following instructions to correctly setup the environment to be able to use the application.
1. Run `git clone https://github.com/Piggun/streaming-data-project.git` in your terminal, to clone the repo at your desired location
2. Run `cd streaming-data-project` to move inside the repo's root folder
3. Run `make create-environment` to create a virtual environment in which to install dependencies
4. Run `source venv/bin/activate` to activate the created environment
5. Run `make install-dependencies` to install the dependencies required by the application to be able to run

Once you have run the above commands you will have to:
1. Create a new `.env` file
2. Populate the `.env` file with your The Guardian API Key and your SQS Queue URL like so ( please replace the items in brackets [ ] ):

   ```
   API_KEY="[Your The Guardian API Key here]"
   SQS_URL="[Your SQS Queue URL here]"
   ```

You have now completed the setup and are ready to run the application.
