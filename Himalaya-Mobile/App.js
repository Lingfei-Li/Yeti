import React from 'react';
import {StackNavigator} from 'react-navigation';
import Routers from './src/Routers';

import {Provider} from 'mobx-react/native';
import store from './src/store';


const AppNavigator = StackNavigator(
  {
    ...Routers,
    Index: {
      screen: Routers.LoginPage.screen,
      // screen: Routers.TransactionListView.screen,
    },
  },
  {
    initialRouteName: 'Index',
    headerMode: 'none',
  }
);

export default () => (
  <Provider store={store}>
    <AppNavigator/>
  </Provider>
);