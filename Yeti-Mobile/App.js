import {DrawerNavigator, StackNavigator} from 'react-navigation'
import Router from './src/Routers'
import SideMenu from './src/pages/SideMenu'



export default DrawerNavigator({
    ...Router
    },
    {
        contentComponent: SideMenu
    }
);


