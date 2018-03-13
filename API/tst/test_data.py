tickets = [
  {
    "ticket_id": "ticket-1",
    "ticket_version": 1,
    "ticket_amount": 25,
    "ticket_price": 59,
    "ticket_type": "Snoqualmie Adult All-day",
    "distributor_id": "lingfeil",
    "distribution_location": "Port 99 10.I5",
    "distribution_start_datetime": "2018-02-04T20:00:00Z",
    "distribution_end_datetime": "2018-02-04T20:30:00Z",
    "status_code": 0
  },
  {
    "ticket_id": "ticket-2",
    "ticket_version": 1,
    "ticket_amount": 10,
    "ticket_price": 59,
    "ticket_type": "Stevens Adult Daytime",
    "distributor_id": "lzexi",
    "distribution_location": "Port 99 10.N5",
    "distribution_start_datetime": "2018-02-05T21:30:00Z",
    "distribution_end_datetime": "2018-02-05T22:00:00Z",
    "status_code": 0
  }
]

orders = [
  {
    "order_id": "order-1",
    "order_version": 1,
    "buyer_id": "lingfeil",
    "ticket_list": [
      {
        "ticket_id": "ticket-2",
        "ticket_version": 1,
        "ticket_amount": 10,
        "ticket_price": 59,
        "ticket_type": "Stevens Adult Daytime",
        "distributor_id": "lzexi",
        "distribution_location": "Port 99 10.N5",
        "distribution_start_datetime": "2018-02-05T21:30:00Z",
        "distribution_end_datetime": "2018-02-05T22:00:00Z",
        "purchase_amount": 3,
        "pickup_status": 0
      },
      {
        "ticket_id": "ticket-2",
        "ticket_version": 1,
        "ticket_amount": 10,
        "ticket_price": 59,
        "ticket_type": "Stevens Adult Daytime",
        "distributor_id": "lzexi",
        "distribution_location": "Port 99 10.N5",
        "distribution_start_datetime": "2018-02-05T21:30:00Z",
        "distribution_end_datetime": "2018-02-05T22:00:00Z",
        "purchase_amount": 5,
        "pickup_status": 1
      }
    ],
    "order_datetime": "2018-02-01T18:30:00Z",
    "expiry_datetime": "2018-02-01T18:40:00Z",
    "payment_id_list": [],
    "status_code": 0
  },
  {
    "order_id": "order-2",
    "order_version": 1,
    "buyer_id": "lingfeil",
    "ticket_list": [
      {
        "ticket_id": "ticket-2",
        "ticket_version": 1,
        "ticket_amount": 10,
        "ticket_price": 59,
        "ticket_type": "Stevens Adult Daytime",
        "distributor_id": "lzexi",
        "distribution_location": "Port 99 10.N5",
        "distribution_start_datetime": "2018-02-05T21:30:00Z",
        "distribution_end_datetime": "2018-02-05T22:00:00Z",
        "purchase_amount": 1,
        "pickup_status": 2
      },
      {
        "ticket_id": "ticket-2",
        "ticket_version": 1,
        "ticket_amount": 10,
        "ticket_price": 59,
        "ticket_type": "Stevens Adult Daytime",
        "distributor_id": "lzexi",
        "distribution_location": "Port 99 10.N5",
        "distribution_start_datetime": "2018-02-05T21:30:00Z",
        "distribution_end_datetime": "2018-02-05T22:00:00Z",
        "purchase_amount": 1,
        "pickup_status": 3
      }
    ],
    "order_datetime": "2018-03-11T18:30:00Z",
    "expiry_datetime": "2018-03-11T18:40:00Z",
    "payment_id_list": [],
    "status_code": 0
  }
]
