import React from 'react';
import { StackNavigator } from 'react-navigation';

import Routers from './src/Routers';


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

export default () => <AppNavigator />;