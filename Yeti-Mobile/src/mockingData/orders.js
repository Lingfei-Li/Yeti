
export const getMockOrders= function() {
    let list = [];

    list.push({
      orderPlacedTime: '2018-02-18T16:32:02-08:00',
      orderPaymentStatus: 0,
      tickets: [
        {
          ticketId: '0-0',
          purchaseAmount: 10
        }
      ]
    });

    return list;
};