const axios = require('axios');

const yeti_api_endpoint = 'https://fxsrb1p4k2.execute-api.us-west-2.amazonaws.com/prod/';
const connectionTimeout = 60;

axios.get('https://fxsrb1p4k2.execute-api.us-west-2.amazonaws.com/prod/ticket')
.then((response) => {
  console.log(response.data);
  const respData = JSON.parse(response.data);
  console.log(respData);

}).catch(error => {
  console.log(JSON.stringify(error))
});

