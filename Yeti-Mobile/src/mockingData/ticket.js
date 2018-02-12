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