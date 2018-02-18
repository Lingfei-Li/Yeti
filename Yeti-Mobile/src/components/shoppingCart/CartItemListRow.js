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


class CartItemListRow extends React.Component{

  getQuantityTextInputValue() {
    if(this.props.quantity) {
      return this.props.quantity.toString();
    } else {
      return "";
    }
  }

  handleTextInputChange(quantityText) {
    quantityText = quantityText.replace('.', '');
    let quantity = 0;
    if(quantityText.length) {
      quantity = parseInt(quantityText);
    }
    this.props.changeTicketQuantityInCart(this.props.ticket.ticketId, quantity);
  }

  render() {

    const ticket = this.props.ticket;

    return (
      <View>
        <Text style={{textAlign: 'center', fontWeight: 'bold', fontSize: 20, marginTop: 20}}>{ticket.ticketType}</Text>
        <Text style={{textAlign: 'center', marginTop: 10}}>{ticket.distributionStartTime} - {ticket.distributionStartTime}</Text>
        <View style={{flexDirection: 'row', justifyContent: 'center', marginTop: 10, marginBottom: 20}}>
          <Text style={{textAlign: 'center'}}>Qty: </Text>
          <TextInput
            style={{width: 30, height: 20, borderColor: 'gray', borderWidth: 1, borderRadius: 2}}
            keyboardType='numeric'
            onChangeText={(quantityText) => this.handleTextInputChange(quantityText)}
            maxLength={2}
            value={this.getQuantityTextInputValue()}
            textAlign={'center'}
          />
          <Text style={{textAlign: 'center'}}> * ${ticket.ticketPrice} = ${ticket.ticketPrice * this.props.quantity}</Text>
        </View>

        <RowSeparator/>

      </View>
    )
  }
}


function mapDispatchToProps(dispatch) {
  return bindActionCreators(Actions, dispatch);
}

export default connect(null, mapDispatchToProps)(CartItemListRow)


const styles = StyleSheet.create({
  quantityDropdown: {
    width: 50,
    marginLeft: 8
  }
}) ;
