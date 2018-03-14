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
import TicketDetails from "./src/pages/TicketDetails";
import Home from './src/pages/Home';
import PaymentPage from "./src/pages/PaymentPage";
import RootErrorBoundary from "expo/src/launch/RootErrorBoundary";
import ShoppingCart from "./src/pages/ShoppingCart";
import configureStore from './src/store/configureStore';
import ShoppingCartTabBarButton from "./src/components/buttons/ShoppingCartTabBarButton";


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
  if(tintColor === '#00699D') {
    return <Image source={require('./src/resources/assets/himalaya.png')} style={[styles.ticketTabBarIcon]} />;
  } else {
    return <Image source={require('./src/resources/assets/himalaya-bw.png')} style={[styles.ticketTabBarIcon]} />;
  }
};


const mainDrawerNavigator = TabNavigator({
  Tickets: {
    screen: ticketStackNav,
    navigationOptions: {
      tabBarLabel:"Tickets",
      tabBarIcon: ({ tintColor }) => getTicketStackTabBarIcon(tintColor)
    }
  },
  Cart: {
    screen: shoppingCartStackNav,
    navigationOptions: {
      tabBarLabel: "Shopping Cart",
      tabBarIcon: ({tintColor}) => <ShoppingCartTabBarButton tintColor={tintColor}/>
    },
  },
  MyOrders: {
    screen: myOrdersStackNav,
    navigationOptions: {
      drawerLabel: "My Orders",
      tabBarIcon: ({tintColor}) => <Icon name='history' size={24} color={tintColor} />
    },
  },
  MyAccount: {
    screen: myAccountStackNav,
    navigationOptions: {
      drawerLabel: "My Account",
      tabBarIcon: ({tintColor}) => <Icon name='user-circle' size={24} color={tintColor}/>
    }
  },
  Debug: {
    screen: debugViewStackNav,
    navigationOptions: {
      drawerLabel: "Debug",
      tabBarIcon: ({tintColor}) => <Icon name='code' size={24} color={tintColor}/>
    }
  }
}, {
  tabBarOptions: {
    activeTintColor: '#00699D',
    inactiveTintColor: 'grey',
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

let store = configureStore();

export default () => (
  <Provider store={store}>
    <RootModalStack />
  </Provider>
);
