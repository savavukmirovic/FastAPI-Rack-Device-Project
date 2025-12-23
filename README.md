# FastAPI-Rack-Device-Project
### Fastapi project for handling racks and devices using REST API-s

To run this application you can run: docker compose up
Other way to run this application you can run: docker build -t fastapi-app
and after that you can run: docker run fastapi-app

Third way to run this application is to use this in terminal: uv run ./main.py

- Swagger documentation can be found on http://0.0.0.0:8000/docs


One rack db object looks like this:
<img width="335" height="399" alt="Screenshot from 2025-12-23 02-12-06" src="https://github.com/user-attachments/assets/53506d44-0815-436a-bc1e-5ac737478d07" />
where rack units must be inserted as Text value "48U" and max_power_capacity_watts like "5000W" text value.

One device object should look like this
<img width="320" height="252" alt="Screenshot from 2025-12-23 02-16-09" src="https://github.com/user-attachments/assets/13362188-5dac-4f9b-b797-491c28333487" />
where power_consumption_watts must be written like Text value "500W" and number_of_taken_units is integer.





Docker image can be found here: https://hub.docker.com/r/savavukmirovic/fastapi
