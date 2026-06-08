Notes for Docker

docker build -t weather-app .

Transfering to other machines- 

Machine A:
docker tag weather-app your-dockerhub-username/weather-app
docker login
docker push your-dockerhub-username/weather-app

Machine B:
docker pull your-dockerhub-username/weather-app
docker run -p 5001:5000 your-dockerhub-username/weather-app
