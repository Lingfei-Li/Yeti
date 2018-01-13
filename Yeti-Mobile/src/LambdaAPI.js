/**
 * Created by Yida Yin on 1/3/18
 */

import React from 'react';
import axios from 'axios';


const connectionTimeOut = 5000;

export default class LambdaAPI {
  static uploadOutlookCode(authCode) {
    return(
      axios({
        method: 'POST',
        url: 'https://fxsrb1p4k2.execute-api.us-west-2.amazonaws.com/prod/user/login/outlook_oauth',
        headers: {
          "content-type": "application/json",
        },
        data: {
          authCode: authCode
        },
        timeout: connectionTimeOut,
      })
    )
  }

  static getAllTransactions(email, token) {
    return (
      axios({
        method: 'GET',
        url: 'https://fxsrb1p4k2.execute-api.us-west-2.amazonaws.com/prod/transactions',
        headers: {
          "Authorization": "Bearer " + token,
          "login-email": email,
        },
        timeout: connectionTimeOut,
      })
    )
  }
}