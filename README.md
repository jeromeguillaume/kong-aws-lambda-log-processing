# AWS Lambda: push Konnect Audit log and Kong GW logs to a S3 Bucket

## Configuration
1) Deploy the AWS Lambda function and get the public URL
2) Konnect CP: Configure the Lambda public URL in Konnect Audit Log and Authorization Header=`Bearer CP_r8q2DLoM2RY4RG2luPvF`
3) Kong GW: Configure the http-log plugin and set the Lambda public URL and Header=`Authorization: Bearer DP_atDUfLaFZlEeJUbt4P58`

The Bearer values are hardcoded in the AWS Lambda

## S3 Bucket
- 2 Directories are created: `Kong_DP`and `Kong_CP`
- The logs are in JSON format and compressed with gzip

![Alt text](/images/1-S3-Directories.png?raw=true "S3 Bucket - Directories")

![Alt text](/images/2-S3-Logs.png?raw=true "S3 Bucket - Files")
