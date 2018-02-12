import * as Actions from '../actions/index'

export const TICKET_LIST_GROUP_BY_PICKUP_TIME = 'Pickup Time';
export const TICKET_LIST_GROUP_BY_TICKET_TYPE = 'Ticket Type';

const TICKET_LIST_GROUP_BY_OPTIONS = [TICKET_LIST_GROUP_BY_PICKUP_TIME, TICKET_LIST_GROUP_BY_TICKET_TYPE];

let defaultState = {
  ticketListGroupByIndex: 0,
  ticketListGroupBy: TICKET_LIST_GROUP_BY_OPTIONS[0],
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
    default:
      return state || defaultState;
  }
}

