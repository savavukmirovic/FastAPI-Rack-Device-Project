# FastAPI-Rack-Device-Project
### Fastapi project for handling racks and devices using REST API-s

- To run this application you can run: docker compose up
- Other way to run this application you can run: docker build -t fastapi-app
and after that you can run: docker run fastapi-app

- Third way to run this application is to use this in terminal: uv run ./main.py

- Swagger documentation can be found on http://0.0.0.0:8000/docs


One rack db object looks like this, where rack units must be inserted as Text value "48U" and max_power_capacity_watts like "5000W" text value:

<img width="335" height="399" alt="Screenshot from 2025-12-23 02-12-06" src="https://github.com/user-attachments/assets/53506d44-0815-436a-bc1e-5ac737478d07" />

One device object should look like this where power_consumption_watts must be written like Text value "500W" and number_of_taken_units is integer.

<img width="320" height="252" alt="Screenshot from 2025-12-23 02-16-09" src="https://github.com/user-attachments/assets/13362188-5dac-4f9b-b797-491c28333487" />

To run algorithm for allocation racks and devices after creating them inside database (using CRUD operations for example) you can go to http://0.0.0.0:8000/devicerackallocation and put device and racks serial numbers together with comma as parameters (do not separate them with space, comma is the only separator) which are primary keys inside database.
Example racks serial numbers provided:rack1A,rack2b
Example devices serial numbers provided:device123,device1A,device3b
One request example: http://0.0.0.0:8000/devicerackallocation?devices_serials_numbers=device123%2Cdevice1A%2Cdevice3b&racks_serials_numbers=rack1A%2Crack2b

<img width="1122" height="595" alt="Screenshot from 2025-12-23 13-34-16" src="https://github.com/user-attachments/assets/79e35805-f88d-4b18-b234-d4d4ab05bd59" />
<img width="1031" height="455" alt="Screenshot from 2025-12-23 13-34-39" src="https://github.com/user-attachments/assets/2bed7dae-b03a-47c1-946e-ddeebb291588" />







Docker image can be found here: https://hub.docker.com/r/savavukmirovic/fastapi
