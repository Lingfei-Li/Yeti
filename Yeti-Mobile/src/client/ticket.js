import axios from 'axios'

const yeti_api_endpoint = 'https://fxsrb1p4k2.execute-api.us-west-2.amazonaws.com/prod/';
const connectionTimeoutMs = 6000;

const concatUrl = function(path) {
  if(path.length === 0) {
    return yeti_api_endpoint;
  }
  if(path[0] === '/') {
    return yeti_api_endpoint + path.substr(1);
  }
  return yeti_api_endpoint + path;
};

export const getAllTickets = function() {
  return(
    axios({
      method: 'GET',
      url: concatUrl('ticket'),
      headers: {
        "content-type": "application/json",
      },
      timeout: connectionTimeoutMs,
    })
  )
};

