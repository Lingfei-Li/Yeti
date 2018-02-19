import React from 'react';
import {
  Text,
  View,
  Dimensions,
  TouchableOpacity,
  StyleSheet, FlatList,
  Platform, Button,
  ScrollView, TextInput
} from 'react-native';
import Icon from 'react-native-vector-icons/FontAwesome';
import {bindActionCreators} from "redux";
import {connect} from "react-redux";
import * as Actions from '../../actions/index'
import log from "../log";
import {TICKET_LIST_GROUP_BY_TICKET_TYPE, TICKET_LIST_GROUP_BY_PICKUP_TIME} from '../../reducers/index'
import RowSeparator from '../RowSeparator';
import {Dropdown} from "react-native-material-dropdown";


class OrderSummaryBanner extends React.Component{

  getTotalPrice() {
    let totalPrice = 0;
    this.props.shoppingCart.forEach((item) => {
      totalPrice += item.purchaseAmount * item.ticket.ticketPrice;
    });
    return totalPrice;
  }

  render() {

    // TODO: handle empty shopping cart

    return (
      <View style={styles.summaryRow}>

        <Text style={{fontWeight: 'bold', fontSize: 18, color: "#666", marginTop: 10}}>Order Summary</Text>
        <Text>{this.props.shoppingCart.length} tickets</Text>
        <Text>Total Price: ${this.getTotalPrice()}</Text>

        <View style={{marginTop: 20}}>
          <Button
            title="Place Order"
            color="#00699D"
            onPress={() => {this.props.navigation.navigate('PaymentPage', {orderId: '12345678901234567890', payingOrder: this.props.shoppingCart})}}
          />
        </View>
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

export default connect(mapStateToProps, mapDispatchToProps)(OrderSummaryBanner)


const styles = StyleSheet.create({
  summaryRow: {
    alignItems: 'center',
    shadowColor: '#ddd',
    shadowOffset: {
      width: 0,
      height: -5
    },
    shadowOpacity: 0.5
  }
}) ;
