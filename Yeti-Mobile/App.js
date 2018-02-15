import {DrawerNavigator, StackNavigator, TabBarBottom, TabNavigator} from 'react-navigation'
import {StyleSheet} from "react-native";
import React from 'react';
import Icon from 'react-native-vector-icons/FontAwesome';
import MyOrders from "./src/pages/MyOrders";
import MyAccount from "./src/pages/MyAccount";
import {Image} from "react-native";
import DebugView from "./src/pages/DebugView";
import Provider from "react-redux/src/components/Provider";
import {combineReducers, createStore} from "redux";
import reducers from './src/reducers/index'
import TicketDetails from "./src/pages/TicketDetails";
import Home from './src/pages/Home';
import PaymentPage from "./src/pages/PaymentPage";
import RootErrorBoundary from "expo/src/launch/RootErrorBoundary";
import ShoppingCart from "./src/pages/ShoppingCart";


const ticketStackNav = StackNavigator(
  {
    Home: {
      name: 'Home',
      description: 'Home',
      screen: Home
    },
    TicketDetails: {
      name: 'TicketDetails',
      description: 'Transaction Details',
      screen: TicketDetails
    },
  }
);

const shoppingCartStackNav = StackNavigator(
  {
    ShoppingCart: {
      name: 'ShoppingCart',
      screen: ShoppingCart
    },
  }
);

const myOrdersStackNav = StackNavigator(
  {
    MyOrders: {
      name: 'MyOrders',
      description: 'Order history',
      screen: MyOrders
    },
  }
);

const myAccountStackNav = StackNavigator(
  {
    MyAccount: {
      name: 'MyAccount',
      description: 'User account',
      screen: MyAccount
    },
  }
);

const debugViewStackNav = StackNavigator(
  {
    DebugView: {
      name: 'DebugView',
      description: 'Debug View',
      screen: DebugView
    },
  }
);


const getTicketStackTabBarIcon = function(tintColor) {
  if(tintColor !== 'gray' && tintColor !== 'black') {
    return <Image source={require('./src/resources/assets/himalaya.png')} style={[styles.ticketTabBarIcon]} />;
  } else {
    return <Image source={require('./src/resources/assets/himalaya-bw.png')} style={[styles.ticketTabBarIcon]} />;
  }
};


const mainDrawerNavigator = DrawerNavigator({
  TicketStack: {
    screen: ticketStackNav,
    navigationOptions: {
      drawerLabel:"Tickets",
      drawerIcon: ({ tintColor }) => getTicketStackTabBarIcon(tintColor)
    }
  },
  ShoppingCartStack: {
    screen: shoppingCartStackNav,
    navigationOptions: {
      drawerLabel: "Shopping Cart",
      drawerIcon: ({tintColor}) => <Icon name='shopping-cart' size={24} color={tintColor} />
    },
  },
  MyOrdersStack: {
    screen: myOrdersStackNav,
    navigationOptions: {
      drawerLabel: "My Orders",
      drawerIcon: ({tintColor}) => <Icon name='history' size={24} color={tintColor} />
    },
  },
  MyAccountStack: {
    screen: myAccountStackNav,
    navigationOptions: {
      drawerLabel: "My Account",
      drawerIcon: ({tintColor}) => <Icon name='user-circle' size={24} color={tintColor}/>
    }
  },
  DebugViewStack: {
    screen: debugViewStackNav,
    navigationOptions: {
      drawerLabel: "Debug",
      drawerIcon: ({tintColor}) => <Icon name='code' size={24} color={tintColor}/>
    }
  }
}, {
  contentOptions : {
    activeTintColor: '#00699D',
    inactiveTintColor: 'black',
  },
});

const RootModalStack = StackNavigator(
  {
    Main: {
      screen: mainDrawerNavigator
    },
    PaymentPage: {
      name: 'PaymentPage',
      description: 'Payment Page',
      screen: PaymentPage
    },
  },
  {
    mode: 'modal',
    headerMode: 'none',
  }
);


const styles = StyleSheet.create({
  ticketTabBarIcon: {
    width: 28,
    height: 28,
  }
}) ;

let store = createStore(reducers);

export default () => (
  <Provider store={store}>
    <RootModalStack />
  </Provider>
);
