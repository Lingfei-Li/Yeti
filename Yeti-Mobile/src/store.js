/**
 * Created by Yida Yin on 1/4/18
 */

import {
  AsyncStorage
} from 'react-native';
import {observable, action, runInAction} from 'mobx';
import {persist, create} from "mobx-persist";

import log from './components/log';
import {timeConverter} from './utils';

class Store {
  @persist @observable email = 'No Email';
  @persist @observable token = '';
  @persist('list') @observable transactions = [];

  @action
  closeTransaction = (TransactionId, TransactionPlatform) => {
    for (let i = 0; i < this.transactions.length; i++) {
      if (this.transactions[i]["TransactionId"] === TransactionId && this.transactions[i]["TransactionPlatform"] === TransactionPlatform) {
        runInAction(() => {
          this.transactions[i]["StatusCode"] = 1;
        });
      }
    }
  };

  @action
  reopenTransaction = (TransactionId, TransactionPlatform) => {
    for (let i = 0; i < this.transactions.length; i++) {
      if (this.transactions[i]["TransactionId"] === TransactionId && this.transactions[i]["TransactionPlatform"] === TransactionPlatform) {
        runInAction(() => {
          this.transactions[i]["StatusCode"] = 0;
        });
      }
    }
  };

  @action
  updateTransaction = (TransactionId, TransactionPlatform, transaction) => {
    for (let i = 0; i < this.transactions.length; i++) {
      if (this.transactions[i]["TransactionId"] === TransactionId && this.transactions[i]["TransactionPlatform"] === TransactionPlatform) {
        runInAction(() => {
          this.transactions[i] = transaction;
        });
      }
    }
  };
}


// new the store to make sure that we export it as a singleton instance.
const store = new Store();
// export the store class directly to reuse it somewhere else independently
export default store;

const hydrate = create({
  storage: AsyncStorage,
  jsonify: true
});

hydrate('store', store)
  .then(() => {
    log.log(`store hydrated, User Email: ${store.email}`);
  });