temp_relay


Run docker app:
docker run -d --network host -p 8500:8500 -e BIND="0.0.0.0:8500" heater_frontend