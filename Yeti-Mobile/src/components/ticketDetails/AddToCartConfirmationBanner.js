import * as Actions from '../../actions/index'
import React from 'react'
import {Animated, StyleSheet, Button, FlatList, Image, Navigator, Picker, Slider, Text, View, TextInput, TouchableOpacity} from "react-native";
import Icon from 'react-native-vector-icons/FontAwesome';
import {bindActionCreators} from "redux";
import {connect} from "react-redux";
import {TICKET_LIST_GROUP_BY_PICKUP_TIME, TICKET_LIST_GROUP_BY_TICKET_TYPE} from "../../reducers/index";
import log from "../log";

class AddToCartConfirmationBanner extends React.Component {

  state = {
    fadeAnim: new Animated.Value(0),  // Initial value for opacity: 0
  };

  componentDidMount() {
    Animated.timing(                  // Animate over time
      this.state.fadeAnim,            // The animated value to drive
      {
        toValue: 1,                   // Animate to opacity: 1 (opaque)
        duration: 500,              // Make it take a while
      }
    ).start();                        // Starts the animation
  }

  getButtonTitle() {
    const ticketAmount = this.props.shoppingCart.reduce((accumulator, orderItem) => {
      return accumulator + orderItem.purchase_amount;
    }, 0);
    const totalPrice = this.props.shoppingCart.reduce((accumulator, orderItem) => {
      return accumulator + orderItem.purchase_amount * orderItem.ticket_price;
    }, 0);
    return `Proceed to checkout (${ticketAmount} tickets) $${totalPrice}`;

  }

  render() {
    return (
      <Animated.View style={{width: '100%', opacity: this.state.fadeAnim}}>
        <View style={styles.confirmationBanner}>
          <Button
            title={this.getButtonTitle()}
            onPress={() => this.props.navigation.navigate('Cart')}
            color="#00699D"
          />
        </View>
      </Animated.View>
    )
  }
}


function mapStateToProps(state) {
  return {
    shoppingCart: state.shoppingCart
  }
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators(Actions, dispatch);
}

export default connect(mapStateToProps, mapDispatchToProps)(AddToCartConfirmationBanner)

const styles = StyleSheet.create({
  confirmationBanner: {
    width: '100%',
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
    borderBottomColor: '#ddd',
    borderBottomWidth: 1,
    shadowColor: '#eee',
    shadowOffset: {
      width: 0,
      height: 5
    },
    shadowOpacity: 0.5
  },
}) ;
