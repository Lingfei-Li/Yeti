/**
 * Created by Yida Yin on 1/4/18
 */

import {
  AsyncStorage
} from 'react-native';
import {observable, action, runInAction} from 'mobx';
import {persist, create} from "mobx-persist";

import log from './components/log';


class Store {
  @persist @observable email = 'No Email';
  @persist @observable token = '';
  @persist('list') @observable transactions = [];
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