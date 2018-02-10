/**
 * Created by Yida Yin on 1/4/18
 */

import LoginPage from './pages/LoginPage';
import TransactionListView from './pages/TransactionListView';
import TransactionDetails from './pages/TransactionDetails';
import DebugView from './pages/DebugView';


const Routers = {
  LoginPage: {
    name: 'Login Page',
    description: 'A card stack',
    screen: LoginPage,
  },
  TransactionListView: {
    name: 'Transactions',
    description: 'Transaction List',
    screen: TransactionListView,
  },
  TransactionDetails: {
    name: 'TransactionDetails',
    description: 'Transaction Details',
    screen: TransactionDetails,
  },
  DebugView: {
    name: 'DebugView',
    screen: DebugView,
  }
};

export default Routers;