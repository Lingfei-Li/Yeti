import Icon from 'react-native-vector-icons/FontAwesome';
import QRCode from 'react-native-qrcode'
import React from 'react'
import {Dimensions, StyleSheet, Button, Text, TouchableOpacity, View} from "react-native";
import Image from 'react-native-scalable-image';
import {bindActionCreators} from "redux";
import {connect} from "react-redux";
import Styles from '../styles'
import CommonStyles from '../styles';
import * as Actions from '../actions/index'
import CartItemList from "../components/shoppingCart/CartItemList";
import log from "../components/log";
import {Dropdown} from "react-native-material-dropdown";
import OpenDrawerButton from "../components/buttons/OpenDrawerButton";
import TicketListButton from "../components/buttons/TicketListButton";


class MyAccount extends React.Component {
  static navigationOptions = ({navigation}) => ({
    headerStyle: CommonStyles.headerStyle,
    headerTitle: <Text style={{fontWeight:'bold', fontSize: 18}}>My Account</Text>,
    headerLeft: <OpenDrawerButton navigation={navigation}/>,
    headerRight: <TicketListButton navigation={navigation}/>
  });

  render() {
    return (
      <View style={styles.container}>
        <Image
          source={require('../resources/assets/himalaya.png')}
          width={Dimensions.get('window').width * 0.4}
        />
        <Text style={{fontSize: 20, fontColor: '#999'}}>{this.props.user.fullName}</Text>
        <Text style={{fontSize: 20, fontColor: '#999'}}>{this.props.user.userId}@</Text>
        <Button
          title="My Orders"
          onPress={() => {this.props.navigation.navigate('MyOrdersStack')}}
        />
        <Button
          title="Edit Profile"
          onPress={() => {alert('Coming soon')}}
        />

        <View style={styles.qrCodeView}>
          <QRCode
            value={this.props.user.userId}
            size={100}
            bgColor='#00699D'
            fgColor='white'/>
        </View>

      </View>
    )
  }
}

function mapStateToProps(state) {
  return {
    user: state.user,
  }
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators(Actions, dispatch);
}

export default connect(mapStateToProps, mapDispatchToProps)(MyAccount)


const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    paddingTop: 50,
    backgroundColor: 'white',
  },
  avatar: {
  },
  qrCodeView: {
    width: 150,
    height: 150,
    marginTop: 50,
    borderWidth: 1,
    borderRadius: 5,
    borderColor: '#eee',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#ccc',
    shadowOffset: {
      width: 0,
      height: 0,
    },
    shadowOpacity: 1

  }

}) ;
