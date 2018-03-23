import axios from 'axios'

const api_endpoint = 'https://fxsrb1p4k2.execute-api.us-west-2.amazonaws.com/prod/order/';
const connectionTimeoutMs = 6000;

function concatUrl(path) {
  if(path.length === 0) {
    return api_endpoint;
  }
  if(path[0] === '/') {
    return api_endpoint + path.substr(1);
  }
  return api_endpoint + path;
};

export const createOrder = function(buyer_email, ticket_list) {
  return(
    axios({
      method: 'POST',
      url: concatUrl('create'),
      headers: {
        "content-type": "application/json",
      },
      data: {
        buyer_email,
        ticket_list
      },
      timeout: connectionTimeoutMs,
    })
  )
};

export const getAllOrdersForUser = function() {
  return(
    axios({
      method: 'GET',
      url: api_endpoint,
      headers: {
        "content-type": "application/json",
        "user_email": "lingfeil@amazon.com"
      },
      timeout: connectionTimeoutMs,
    })
  )
};

