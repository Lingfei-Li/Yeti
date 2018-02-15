import log from "../components/log";


export const TOGGLE_TICKET_LIST_GROUP_BY = 'TOGGLE_TICKET_LIST_GROUP_BY';
export const UPDATE_TICKET_SEARCH_TEXT = 'UPDATE_TICKET_SEARCH_TEXT';
export const ADD_TICKET_TO_CART = 'ADD_TICKET_TO_CART';

export function toggleTicketListGroupBy() {
  log.info('Action: toggleTicketListGroupBy');

  return {
    type: TOGGLE_TICKET_LIST_GROUP_BY
  };
}

export function updateTicketSearchText(text) {
  log.info('Action: updateTicketSearchText');

  return {
    type: UPDATE_TICKET_SEARCH_TEXT,
    text: text
  };
}

export function addTicketToCart(ticket, purchaseAmount) {
  log.info('Action: addTicketToCart');

  return {
    type: ADD_TICKET_TO_CART,
    ticket,
    purchaseAmount,
  };
}
