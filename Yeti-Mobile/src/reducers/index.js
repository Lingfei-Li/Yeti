import * as Actions from '../actions/index'
import log from "../components/log";

export const TICKET_LIST_GROUP_BY_PICKUP_TIME = 'Pickup Time';
export const TICKET_LIST_GROUP_BY_TICKET_TYPE = 'Ticket Type';

const TICKET_LIST_GROUP_BY_OPTIONS = [TICKET_LIST_GROUP_BY_PICKUP_TIME, TICKET_LIST_GROUP_BY_TICKET_TYPE];

const defaultState = {
  userId: 'lingfeil',
  ticketList: [],
  ticketListGroupByIndex: 0,
  ticketListGroupBy: TICKET_LIST_GROUP_BY_OPTIONS[0],
  ticketSearchText: "",
  orderList: [],
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
    case Actions.SET_OR_REFRESH_TICKET_LIST:
      newState.ticketList = action.ticketList;
      return newState;

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
      const ticket = action.ticket;
      let newCartItem = {
        purchase_amount: action.purchase_amount,
        ticket_id: ticket.ticket_id,
        ticket_type: ticket.ticket_type,
        ticket_version: ticket.ticket_version,
        distribution_start_datetime: ticket.distribution_start_datetime,
        distribution_end_datetime: ticket.distribution_end_datetime,
        distribution_location: ticket.distribution_location,
        ticket_price: ticket.ticket_price
      };

      for(let i = newState.shoppingCart.length - 1; i >= 0; i --) {
        if(newState.shoppingCart[i].ticket_id === newCartItem.ticket_id) {
          newCartItem.purchase_amount += newState.shoppingCart[i].purchase_amount;
          newState.shoppingCart.splice(i, 1);
        }
      }

      newState.shoppingCart.push(newCartItem);
      log.info(`add ${newCartItem.purchase_amount} ${newCartItem.ticket_type} to cart`);
      return newState;

    case Actions.CLEAR_SHOPPING_CART:
      newState.shoppingCart = [];
      return newState;

    case Actions.CHANGE_TICKET_QUANTITY_IN_CART:
      for(let i = newState.shoppingCart.length - 1; i >= 0; i --) {
        if(newState.shoppingCart[i].ticket_id === action.ticketId) {
          newState.shoppingCart[i].purchase_amount = action.quantity;
        }
      }

      log.info(`changed ticketId ${action.ticketId} quantity to ${action.quantity}`);
      return newState;

    case Actions.DELETE_TICKET_FROM_CART:
      for(let i = newState.shoppingCart.length - 1; i >= 0; i --) {
        if(newState.shoppingCart[i].ticketId === action.ticketId) {
          newState.shoppingCart.splice(i, 1);
        }
      }

      log.info(`delete ticketId ${action.ticketId} from cart`);
      return newState;

    case Actions.SET_OR_REFRESH_ORDER_LIST:
      newState.orderList = action.orderList;
      return newState;

    default:
      return state || defaultState;
  }
}

