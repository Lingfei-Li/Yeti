import Icon from 'react-native-vector-icons/FontAwesome';
import React from 'react'
import {StyleSheet, Button, Image, Text, TouchableOpacity, View} from "react-native";
import {bindActionCreators} from "redux";
import {connect} from "react-redux";
import Styles from '../styles'
import HeaderSearchBar from "../components/HeaderSearchBar";
import CommonStyles from '../styles';
import * as Actions from '../actions/index'
import OpenDrawerButton from '../components/headerButton/OpenDrawerButton';
import TicketListButton from '../components/headerButton/TicketListButton';
import CartItemList from "../components/shoppingCart/CartItemList";
import log from "../components/log";


class ShoppingCart extends React.Component {
  static navigationOptions = ({navigation}) => ({
    headerTitle: <Text style={{fontWeight:'bold', fontSize: 18}}>Shopping Cart</Text>,
    headerLeft: <OpenDrawerButton navigation={navigation}/>,
    headerRight: <TicketListButton navigation={navigation}/>
  });


  render() {
    log.info(this.props.shoppingCart);
    return (
      <View style={styles.container}>
        <CartItemList navigation={this.props.navigation}/>
        <Button
          title="Place Order"
          onPress={() => {this.props.navigation.navigate('PaymentPage', {orderId: '12345678901234567890', payingOrder: this.props.shoppingCart})}}
        />
      </View>
  )
  }
}

function mapStateToProps(state) {
  return {
    shoppingCart: state.shoppingCart,
  }
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators(Actions, dispatch);
}

export default connect(mapStateToProps, mapDispatchToProps)(ShoppingCart)

const styles = StyleSheet.create({
  menuContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: 10,
    backgroundColor: '#ecf0f1',
  },
  paragraph: {
    margin: 24,
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
    color: '#34495e',
  },
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
  },
}) ;
