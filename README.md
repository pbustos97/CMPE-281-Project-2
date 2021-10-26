# Receipt Rekognition Lambda
### [Project link]() Fill later
### [Documentation]() Fill later

## [San Jose State University](http://www.sjsu.edu/)
## Course: [Cloud Technologies](http://info.sjsu.edu/web-dbgen/catalog/courses/CMPE281.html)
## Professor: [Sanjay Garje](https://www.linkedin.com/in/sanjaygarje/)
## Student: [Patrick Bustos](https://www.linkedin.com/in/patrickdbustos/)
## Project Introduction
This project is a section of [this repository](). This repository handles everything that has to do with Rekognition. Images of receipts should ideally be cropped to include Total amount, Tax amount, and store name. If there are too much text on the receipt, images should be cropped to Include Total amount and Tax amount if found on receipt.
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
- Software for testing this repository
  - AWS API Gateway, S3, Lambda
- How to setup repository for testing
  - (Code should not be using third party packages)
  - Create a Lambda function with any name
  - Copy and Paste one of the 'receipt' .py files into the default Lambda function
    - This file should be called lambda_handler.py
  - Upload all the .py files that do not have 'receipt' in the name to the Lambda folder
  - When creating a test, make sure that the 'bucket', 'file', and 'userId' query parameters are in the test.
    - This is important for the functions to work
  - Run the tests, output should have the relevant data if the data was uploaded correctly
  
### Issues
- Rekognition only detects a max of 50 items
  - Long receipts with many items should be cropped to the total and tax amounts only
- Rekognition can only detect images coming from a bucket in the same region
  - Could be circumvented with direct upload but it isn't worth it increasing internal bandwidth
- If image is too large, might timeout? (Need to test on live deployment)

### Completed Rekognition detections
- Standard store receipts
