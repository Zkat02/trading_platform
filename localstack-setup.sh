#!/bin/sh
echo "Initializing localstack s3"

awslocal ses verify-email-identity --email-address zkatdjango@gmail.com

aws configure set aws_access_key_id localstack
aws configure set aws_secret_access_key localstack

echo "[default]" > ~/.aws/config
echo "region = us-east-1" >> ~/.aws/config
echo "output = json" >> ~/.aws/config
