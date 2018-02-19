import * as Actions from '../actions/index'
import log from "../components/log";

export const TICKET_LIST_GROUP_BY_PICKUP_TIME = 'Pickup Time';
export const TICKET_LIST_GROUP_BY_TICKET_TYPE = 'Ticket Type';

const TICKET_LIST_GROUP_BY_OPTIONS = [TICKET_LIST_GROUP_BY_PICKUP_TIME, TICKET_LIST_GROUP_BY_TICKET_TYPE];

const defaultState = {
  userId: 'lingfeil',
  ticketListGroupByIndex: 0,
  ticketListGroupBy: TICKET_LIST_GROUP_BY_OPTIONS[0],
  ticketSearchText: "",
  shoppingCart: [],
  user: {
    userId: 'lingfeil',
    fullName: 'Lingfei Li'
  }
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

    case Actions.SET_TICKET_LIST_GROUP_BY_PICKUP_TIME:
      newState.ticketListGroupByIndex = 0;
      newState.ticketListGroupBy = TICKET_LIST_GROUP_BY_OPTIONS[newState.ticketListGroupByIndex];
      return newState;

    case Actions.SET_TICKET_LIST_GROUP_BY_TICKET_TYPE:
      newState.ticketListGroupByIndex = 1;
      newState.ticketListGroupBy = TICKET_LIST_GROUP_BY_OPTIONS[newState.ticketListGroupByIndex];
      return newState;

    case Actions.UPDATE_TICKET_SEARCH_TEXT:
      newState.ticketSearchText = action.text;
      log.info('updating ticket search text: ' + action.text);
      return newState;

    case Actions.ADD_TICKET_TO_CART:
      let newCartItem = {purchaseAmount: action.purchaseAmount, ticket: cloneObject(action.ticket)};

      for(let i = newState.shoppingCart.length - 1; i >= 0; i --) {
        if(newState.shoppingCart[i].ticket.ticketId === action.ticket.ticketId) {
          newCartItem.purchaseAmount += newState.shoppingCart[i].purchaseAmount;
          newState.shoppingCart.splice(i, 1);
        }
      }

      newState.shoppingCart.push(newCartItem);
      log.info(`add ${action.purchaseAmount} ${action.ticket.ticketType} to cart`);
      return newState;

    case Actions.CHANGE_TICKET_QUANTITY_IN_CART:
      for(let i = newState.shoppingCart.length - 1; i >= 0; i --) {
        if(newState.shoppingCart[i].ticket.ticketId === action.ticketId) {
          newState.shoppingCart[i].purchaseAmount = action.quantity;
        }
      }

      log.info(`changed ticketId ${action.ticketId} quantity to ${action.quantity}`);
      return newState;

    case Actions.DELETE_TICKET_FROM_CART:
      for(let i = newState.shoppingCart.length - 1; i >= 0; i --) {
        if(newState.shoppingCart[i].ticket.ticketId === action.ticketId) {
          newState.shoppingCart.splice(i, 1);
        }
      }

      log.info(`delete ticketId ${action.ticketId} from cart`);
      return newState;

    default:
      return state || defaultState;
  }
}

