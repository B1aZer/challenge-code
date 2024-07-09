cd ../app
aws ecr get-login-password --region region | docker login --username AWS --password-stdin 123456789012.dkr.ecr.region.amazonaws.com
docker build -t flask-app .
docker tag flask-app:latest 123456789012.dkr.ecr.region.amazonaws.com/bestappever:latest

