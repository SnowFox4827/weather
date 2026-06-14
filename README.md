Notes for Docker

docker build -t weather-app .

Transfering to other machines- 

Machine A:
docker tag weather-app your-dockerhub-username/weather-app
docker login
docker push your-dockerhub-username/weather-app

Machine B:
docker pull your-dockerhub-username/weather-app
docker run -d -p 5001:5000 your-dockerhub-username/weather-app

Use Watch Tower to automatically keep the container being used up to date, looking into kubernetes
https://containrrr.dev/watchtower/
