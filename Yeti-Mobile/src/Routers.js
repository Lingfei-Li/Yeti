import HomePage from './pages/Home';
import UserAccountPage from './pages/UserAccount';
import OrderHistoryPage from './pages/OrderHistory';
import LoginPage from './pages/Login';
import DebugView from './pages/DebugView';


const Routers = {
    UserAccountPage: {
        screen: UserAccountPage
    },
    HomePage: {
        screen: HomePage
    },
    OrderHistoryPage: {
        screen: OrderHistoryPage
    },
    LoginPage: {
        screen: LoginPage
    },
    DebugView: {
        screen: DebugView
    }
};

export default Routers;