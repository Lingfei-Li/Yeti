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
        url: 'https://d4g1nmfov8.execute-api.us-west-2.amazonaws.com/prod/user/login/outlook_oauth',
        // url: 'http://httpbin.org/post',
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

  static getAllTransactions() {
    return (
      null
    )
  }
}