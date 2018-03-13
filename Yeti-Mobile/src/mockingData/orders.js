const ticketTypes = [
  'Snoqualmie Adult Daily',
  'Stevens Adult Daily',
  'Crystal Mountain Adult Daily',
];

const distributionStartTime = [
  '2018-02-01T11:00:00-08:00',
  '2018-02-25T11:00:00-08:00',
  '2018-02-26T16:00:00-08:00',
  '2018-02-27T15:00:00-08:00',
  '2018-02-28T15:30:00-08:00',
  '2018-03-11T15:00:00-08:00'
];

const distributionEndTime = [
  '2018-02-01T11:30:00-08:00',
  '2018-02-25T11:30:00-08:00',
  '2018-02-26T16:30:00-08:00',
  '2018-02-27T15:30:00-08:00',
  '2018-02-28T16:00:00-08:00',
  '2018-03-12T15:30:00-08:00'
];

export const getMockOrders= function() {
    let list = [];

    list.push(
      {
        orderId: 'orderId-0',
        orderPlacedTime: '2018-02-18T16:32:02-08:00',
        orderPaymentStatus: 0,
        orderItems: [
          {
            ticket: {
              ticketId: 'ticketId-0',
              ticketType: ticketTypes[0],
              ticketPrice: 59,
              distributionStartTime: distributionStartTime[2],
              distributionEndTime: distributionEndTime[2],
            },
            purchaseAmount: 5,
            pickupStatus: 0
          },
          {
            ticket: {
              ticketId: 'id-1',
              ticketType: ticketTypes[1],
              ticketPrice: 59,
              distributionStartTime: distributionStartTime[3],
              distributionEndTime: distributionEndTime[3],
            },
            purchaseAmount: 10,
            pickupStatus: 0
          }
        ]
      },
      {
        orderId: 'orderId-1',
        orderPlacedTime: '2018-02-07T16:32:02-08:00',
        orderPaymentStatus: 0,
        orderItems: [
          {
            ticket: {
              ticketId: 'ticketId-1',
              ticketType: ticketTypes[2],
              ticketPrice: 59,
              distributionStartTime: distributionStartTime[2],
              distributionEndTime: distributionEndTime[2],
            },
            purchaseAmount: 10,
            pickupStatus: 0
          }
        ]
      }
    );

    return list;
};