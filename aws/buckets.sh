#!/usr/bin/env bash
echo "Creating's bucket"
aws --endpoint-url=http://localhost:4566 s3api create-bucket --bucket images
echo "Buckets"
aws --endpoint-url=http://localhost:4566 s3 ls
