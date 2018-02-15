import * as Actions from '../actions/index'
import log from "../components/log";

export const TICKET_LIST_GROUP_BY_PICKUP_TIME = 'Pickup Time';
export const TICKET_LIST_GROUP_BY_TICKET_TYPE = 'Ticket Type';

const TICKET_LIST_GROUP_BY_OPTIONS = [TICKET_LIST_GROUP_BY_PICKUP_TIME, TICKET_LIST_GROUP_BY_TICKET_TYPE];

let defaultState = {
  ticketListGroupByIndex: 0,
  ticketListGroupBy: TICKET_LIST_GROUP_BY_OPTIONS[0],
  ticketSearchText: "",
  shoppingCart: [],
};

const cloneObject = function(obj) {
  return JSON.parse(JSON.stringify(obj));
};

export default function(state=defaultState, action) {
  let newState = cloneObject(state);

  switch(action.type) {
    case Actions.TOGGLE_TICKET_LIST_GROUP_BY:
      const newIndex = (newState.ticketListGroupByIndex + 1 ) % TICKET_LIST_GROUP_BY_OPTIONS.length;
      newState.ticketListGroupByIndex = newIndex;
      newState.ticketListGroupBy = TICKET_LIST_GROUP_BY_OPTIONS[newIndex];
      return newState;
    case Actions.UPDATE_TICKET_SEARCH_TEXT:
      newState.ticketSearchText = action.text;
      log.info('updating ticket search text: ' + action.text);
      return newState;
    case Actions.ADD_TICKET_TO_CART:
      const cartItem = {ticket: action.ticket, purchaseAmount: action.purchaseAmount};
      newState.shoppingCart.push(cartItem);
      log.info(`add ${action.purchaseAmount} ${action.ticket.ticketType} to cart`);
      return newState;
    default:
      return state || defaultState;
  }
}

