import Icon from 'react-native-vector-icons/FontAwesome';
import React from 'react'
import {StyleSheet, Button, Image, Text, TouchableOpacity, View} from "react-native";
import {bindActionCreators} from "redux";
import {connect} from "react-redux";
import Styles from '../styles'
import CommonStyles from '../styles';
import * as Actions from '../actions/index'
import OpenDrawerButton from '../components/buttons/OpenDrawerButton';
import TicketListButton from '../components/buttons/TicketListButton';
import CartItemList from "../components/shoppingCart/CartItemList";
import log from "../components/log";
import {Dropdown} from "react-native-material-dropdown";
import HomeButton from "../components/buttons/HomeButton";


class ShoppingCart extends React.Component {
  static navigationOptions = ({navigation}) => ({
    headerStyle: CommonStyles.headerStyle,
    headerTitle: <Text style={{fontWeight:'bold', fontSize: 18}}>Shopping Cart</Text>,
    headerLeft: <HomeButton navigation={navigation}/>,
  });

  render() {

    return (
      <View style={styles.container}>
        <CartItemList navigation={this.props.navigation}/>
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
  container: {
    flex: 1,
    backgroundColor: 'white',
    alignItems: 'center',
  },
}) ;
