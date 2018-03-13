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

export const getMockTickets = function() {
    let list = [];

    for(let i = 0; i < distributionStartTime.length; i ++) {
      for(let j = 0; j < ticketTypes.length; j ++) {
        const ticket = {
          ticketId: `${i}-${j}`,
          ticketType: ticketTypes[j],
          ticketAmount: 10*((i+j)%5+1),
          ticketPrice: 59,
          distributionStartTime: distributionStartTime[i],
          distributionEndTime: distributionEndTime[i],
        };
        list.push(ticket);
      }
    }

    return list;
};