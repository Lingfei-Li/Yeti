const ticketTypes = [
  'Snoqualmie Adult Daily',
  'Stevens Adult Daily',
  'Crystal Mountain Adult Daily',
];

const distributionStartTime = [
  '2/2 Fri 11:00',
  '2/5 Mon 16:00',
  '2/6 Tue 15:00',
  '2/7 Tue 15:30',
  '2/9 Fri 15:00',
];

const distributionEndTime = [
  '2/2 Fri 11:30',
  '2/5 Mon 16:30',
  '2/6 Tue 15:30',
  '2/7 Tue 16:00',
  '2/9 Fri 15:30',
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
              distributionStartTime: distributionStartTime[0],
              distributionEndTime: distributionEndTime[0],
            },
            purchaseAmount: 5,
            pickupStatus: 0
          },
          {
            ticket: {
              ticketId: 'id-1',
              ticketType: ticketTypes[1],
              ticketPrice: 59,
              distributionStartTime: distributionStartTime[1],
              distributionEndTime: distributionEndTime[1],
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