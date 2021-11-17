# Receipt Rekognition Lambda
### [Project link](https://master.d350pue95ehqmp.amplifyapp.com/)
### [Documentation](https://docs.google.com/document/d/1IlVUQphtsvE4nSn3mD8FkTK-arvkAeO-Rf9J3Ciekwk)

## [San Jose State University](http://www.sjsu.edu/)
## Course: [Cloud Technologies](http://info.sjsu.edu/web-dbgen/catalog/courses/CMPE281.html)
## Professor: [Sanjay Garje](https://www.linkedin.com/in/sanjaygarje/)
## Student: [Patrick Bustos](https://www.linkedin.com/in/patrickdbustos/)
## Project Introduction
This project is a section of this [repository](https://github.com/bfkwong/itemize). This repository handles everything that has to do with Rekognition and Lex. For Rekognition, images of receipts should ideally be cropped to include Total amount, Tax amount, and store name. If there is too much text on the receipt, images should be cropped to include Total amount and Tax amount if found on receipt. Ideally Lex should be able to detect wrong inputs for each type but I created a Lambda function that should validate all inputs through string modification with regex. W2 forms are also an acceptable format though it hasn't been tested as much as regular store receipts.
## Screenshots
- Lambda examples
  - Successful detection ![Success](https://i.imgur.com/tX7yfoe.png)
  - Invalid input parameters ![Logged In](https://i.imgur.com/MlkbSzA.png)
# Pre-requisites to setup
- AWS Services for production
  - AWS S3, Transfer Acceleration
  - AWS CloudFront
  - AWS Lambda
  - AWS DynamoDB
  - AWS SNS
  - AWS SES
  - AWS CloudWatch
  - AWS Route 53
  - AWS Rekognition
  - AWS Amplify
  - AWS API Gateway
  - AWS Lex
- Software for testing this repository
  - AWS API Gateway, S3, Lambda, Lex
- How to setup repository for testing
  - (Code should not be using third party packages)
  - Create two Lambda functions with any name
  - Copy and Paste the code in the `receipt_sales_tax.py` file into the default Lambda function of one of the created Lambdas
    - This file inside of the Lambda console should be called lambda_handler.py
  - Upload all the common .py files from the common folder to the Lambda console folder containing the file lambda_handler.py
  - Copy and Paste the code in the `lex-register-user.py` file into the other created Lambda
  - When creating a test for the Rekognition Lambda, make sure that the 'category', file', and 'userId' query parameters are in the test.
    - This is important for the Rekognition Lambda to work
  - When creating a test for the Lex Lambda, make sure that Lex is properly set up first.
    - Use the v1 console of Lex in order to create the chatbot.
    - For the Lex settings, on one of the Intents, have the settings look like this [image](https://i.imgur.com/5vo6pCi.png).
      - Lambda Initialization and Validation field and the Fulfillment field should be linked to the Lambda function created for the Lex bot.
    - Test the chat bot using whatever appropriate inputs you want, then go into Cloud Watch and look for an entry that says `[EVENT] event: ` inside of the Lex's Lambda logs. 
    - Copy the settings from that Cloud Watch entry into the Lex Lambda test and fix the formatting to one that will not show errors.
  - Run the tests, output should have the relevant data if the data was uploaded correctly
  
### Issues
- Rekognition only detects a max of 50 items
  - Long receipts with many items should be cropped to the total and tax amounts only
- Rekognition can only detect images coming from a bucket in the same region
  - Could be circumvented with direct upload but it isn't worth it increasing internal bandwidth
- If image is too large, might timeout? (Need to test on live deployment)
- Lex doesn't detect some invalid inputs, need to account for wrong inputs

### Completed Rekognition detections
- Standard store receipts
- One W2 form, PDF style

### Completed Lex functionality
- Returns input of user through Lex
- Basic numerical validation