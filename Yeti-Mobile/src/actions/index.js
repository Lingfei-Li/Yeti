import log from "../components/log";


export const SET_OR_REFRESH_TICKET_LIST = 'SET_OR_REFRESH_TICKET_LIST';
export const TOGGLE_TICKET_LIST_GROUP_BY = 'TOGGLE_TICKET_LIST_GROUP_BY';
export const SET_TICKET_LIST_GROUP_BY_PICKUP_TIME = 'SET_TICKET_LIST_GROUP_BY_PICKUP_TIME';
export const SET_TICKET_LIST_GROUP_BY_TICKET_TYPE = 'SET_TICKET_LIST_GROUP_BY_TICKET_TYPE';
export const UPDATE_TICKET_SEARCH_TEXT = 'UPDATE_TICKET_SEARCH_TEXT';
export const ADD_TICKET_TO_CART = 'ADD_TICKET_TO_CART';
export const CHANGE_TICKET_QUANTITY_IN_CART = 'CHANGE_TICKET_QUANTITY_IN_CART';
export const DELETE_TICKET_FROM_CART = 'DELETE_TICKET_FROM_CART';

export function setOrRefreshTicketList(ticketList) {
  log.info('Action: setOrRefreshTicketsList');

  return {
    type: SET_OR_REFRESH_TICKET_LIST,
    ticketList
  };
}

export function toggleTicketListGroupBy() {
  log.info('Action: toggleTicketListGroupBy');

  return {
    type: TOGGLE_TICKET_LIST_GROUP_BY
  };
}

export function setTicketListGroupByPickupTime() {
  log.info('Action: setTicketListGroupByPickupTime');

  return {
    type: SET_TICKET_LIST_GROUP_BY_PICKUP_TIME
  };
}

export function setTicketListGroupByTicketType() {
  log.info('Action: setTicketListGroupByTicketType');

  return {
    type: SET_TICKET_LIST_GROUP_BY_TICKET_TYPE
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

export function changeTicketQuantityInCart(ticketId, quantity) {
  log.info('Action: changeTicketQuantityInCart');

  return {
    type: CHANGE_TICKET_QUANTITY_IN_CART,
    ticketId,
    quantity
  };
}

export function deleteTicketFromCart(ticketId) {
  log.info('Action: deleteTicketFromCart');

  return {
    type: DELETE_TICKET_FROM_CART,
    ticketId
  };
}
