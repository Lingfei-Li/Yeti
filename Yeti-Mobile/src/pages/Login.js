import React from 'react';
import {
    Button,
    StyleSheet,
    Text,
    View,
    ImageBackground, Image,
} from 'react-native';

// import log from '../components/log';


export default class LoginPage extends React.Component {
    static navigationOptions = {
        drawerLabel: 'Login',
        drawerIcon: ({tintColor}) => (
            <Image
                source={require('../resources/assets/login.png')}
                style={[Styles.icon, {tintColor: tintColor}]}
            />
        )
    };

    render() {
        // log.info("Entering login page");
        return (
            <View>
                <Text>This is a Login page!</Text>
            </View>
        );
    }
}

