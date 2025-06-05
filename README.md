## Railway Ticket Reservation API

This project is a REST API for booking railway tickets. It uses Python with FastAPI and a relational database. The API follows these rules:
1. 63 confirmed berths
2. 9 RAC berths (18 passengers, 2 per side-lower berth)
3. 10 waiting list tickets
4. Children under 5 do not get a berth
5. Lower berth priority for:
   1. Age 60 or older
   2. Women with children
  
## Features
1. Book ticket
2. Cancel ticket
3. See booked tickets
4. See available tickets

## API Endpoints

| Action         | Verb | Path                                      |
|----------------|------|-------------------------------------------|
| Book ticket    | POST | `/api/v1/tickets/book`                    |
| Cancel ticket  | POST | `/api/v1/tickets/cancel/{ticketId}`       |
| Booked list    | GET  | `/api/v1/tickets/booked`                  |
| Available list | GET  | `/api/v1/tickets/available`               |


      
