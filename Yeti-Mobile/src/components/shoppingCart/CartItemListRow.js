import React from 'react';
import {
  Animated,
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

  state = {
    quantityText: this.props.quantity.toString(),
    fadeAnim: new Animated.Value(this.getOpacity()),  // Initial value for opacity: 1
  };

  getOpacity() {
    if(this.props.quantity !== 0) {
      return 1;
    }
    else {
      return 0.2;
    }
  }

  handleTextInputChange(quantityText) {
    quantityText = quantityText.replace('.', '');
    this.setState({quantityText: quantityText})
  }

  handleTextInputBlur(e) {
    const text = e.nativeEvent.text;
    if(text && text.length > 0 && text.trim() !== '0') {
      this.props.changeTicketQuantityInCart(this.props.ticket.ticketId, parseInt(text));
      this.setState({
        quantityText: text
      });
      this.animateOpacity(1);
    }
     else {
      this.animateOpacity(0.2);
      this.props.changeTicketQuantityInCart(this.props.ticket.ticketId, 0);
      this.setState({
        quantityText: '0'
      })
    }
  }

  animateOpacity(toValue) {
    Animated.timing(                  // Animate over time
      this.state.fadeAnim,            // The animated value to drive
      {
        toValue,
        duration: 300,              // Make it take a while
      }
    ).start();                        // Starts the animation

  }

  render() {

    const ticket = this.props.ticket;

    return (
      <View>
        <Animated.View style={{opacity: this.state.fadeAnim}}>
          <Text style={{textAlign: 'center', fontWeight: 'bold', fontSize: 20, marginTop: 20}}>{ticket.ticketType}</Text>
          <Text style={{textAlign: 'center', marginTop: 10}}>{ticket.distributionStartTime} - {ticket.distributionStartTime}</Text>
          <View style={{flexDirection: 'row', justifyContent: 'center', marginTop: 10, marginBottom: 20}}>
            <Text style={{textAlign: 'center'}}>Qty: </Text>
            <TextInput
              style={{width: 30, height: 20, borderColor: 'gray', borderWidth: 1, borderRadius: 2}}
              keyboardType='numeric'
              onChangeText={(text) => this.handleTextInputChange(text)}
              onEndEditing={(e) => this.handleTextInputBlur(e)}
              maxLength={2}
              textAlign={'center'}
              value={this.state.quantityText}
            />
            <Text style={{textAlign: 'center'}}> * ${ticket.ticketPrice} = ${ticket.ticketPrice * this.props.quantity}</Text>
          </View>
        </Animated.View>

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
