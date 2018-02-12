import log from "../components/log";


export const TOGGLE_TICKET_LIST_GROUP_BY = 'TOGGLE_TICKET_LIST_GROUP_BY';

export function toggleTicketListGroupBy() {
  log.info('Action: toggleTicketListGroupBy');

  return {
    type: TOGGLE_TICKET_LIST_GROUP_BY
  };
}

