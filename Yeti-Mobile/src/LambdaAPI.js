import React from 'react';
import axios from 'axios';


const connectionTimeOut = 20000;

export default class LambdaAPI {
  static getAllTickets(userId, token) {
    return (
      axios({
        method: 'POST',
        url: 'https://fxsrb1p4k2.execute-api.us-west-2.amazonaws.com/prod/transactions/reopen',
        headers: {
          "Authorization": "Bearer " + token,
          "login-email": email,
        },
        data: {
          transactionId: transactionId,
          transactionPlatform: transactionPlatform
        },
        timeout: connectionTimeOut,
      })
    )
  }
}