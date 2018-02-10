/**
 * Created by Yida Yin on 1/3/18
 */

import React from 'react';
import axios from 'axios';


const connectionTimeOut = 20000;

export default class LambdaAPI {
  static uploadOutlookCode(authCode) {
    return(
      axios({
        method: 'POST',
        url: 'https://fxsrb1p4k2.execute-api.us-west-2.amazonaws.com/prod/auth/outlook-oauth',
        headers: {
          "content-type": "application/json",
        },
        data: {
          auth_code: authCode
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

  static getTransactionDetail(email, token, transactionPlatform, transactionId) {
    return (
      axios({
        method: 'GET',
        url: `https://fxsrb1p4k2.execute-api.us-west-2.amazonaws.com/prod/transactions/details/${transactionPlatform}/${transactionId}`,
        headers: {
          "Authorization": "Bearer " + token,
          "login-email": email,
        },
        timeout: connectionTimeOut,
      })
    )
  }

  static closeTransaction(email, token, transactionId, transactionPlatform) {
    return (
      axios({
        method: 'POST',
        url: 'https://fxsrb1p4k2.execute-api.us-west-2.amazonaws.com/prod/transactions/close',
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

  static reopenTransaction(email, token, transactionId, transactionPlatform) {
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