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
    fadeAnim: new Animated.Value(this.getOpacity()),
    deleteButtonWidth: new Animated.Value(this.getDeleteButtonWidth()),
  };

  componentDidUpdate(prevProps, prevState, prevContext) {
    // Due to list row reuse, must update the component state manually.
    // The props have been changed, but the states wil not change automatically
    if(prevProps.ticket.ticketId !== this.props.ticket.ticketId) {
      if(prevProps.quantity !== this.props.quantity) {    // condition check is necessary or there'll be an infinite component update loop
        this.setState({
          quantityText: this.props.quantity.toString(),
          fadeAnim: new Animated.Value(this.getOpacity()),
          deleteButtonWidth: new Animated.Value(this.getDeleteButtonWidth()),
        })
      }
    }
  }

  getOpacity() {
    if(this.props.quantity !== 0) {
      return 1;
    }
    else {
      return 0.2;
    }
  }

  getDeleteButtonWidth() {
    if(this.props.quantity !== 0) {
      return 0;
    }
    else {
      return 50;
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
      this.animateDeleteButtonWidth(0);
    }
     else {
      this.animateOpacity(0.2);
      this.animateDeleteButtonWidth(50);
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

  animateDeleteButtonWidth(toValue) {
    Animated.timing(
      this.state.deleteButtonWidth,
      {
        toValue,
        duration: 300,
      }
    ).start();
  }

  getDeleteButton() {
    let icon = null;
    if(this.props.quantity === 0) {
      icon = (
        <Icon name="trash" size={22} style={{color: '#eee'}}/>
      );
    }

    // Always return a component even if it's empty.
    // If return a null when deletion is not allowed, the button will be covered beneath the other components and become invisible
    return (
      <Animated.View
        style={{height: '100%', width: this.state.deleteButtonWidth, right: 0, position: 'absolute', justifyContent: 'center', alignItems: 'center'}}
      >
        <TouchableOpacity
          onPress={() => this.props.deleteTicketFromCart(this.props.ticket.ticketId) }
          style={{height: '100%', width: '100%', right: 0, backgroundColor: '#ff4444', opacity: 0.8,  position: 'absolute', justifyContent: 'center', alignItems: 'center'}}
        >
          {icon}
        </TouchableOpacity>
      </Animated.View>
    )
  }

  render() {

    const ticket = this.props.ticket;

    return (
      <View>

        <Animated.View style={{opacity: this.state.fadeAnim}}>
          <Text style={{textAlign: 'center', fontWeight: 'bold', fontSize: 20, marginTop: 20}}>{ticket.ticket_type}</Text>
          <Text style={{textAlign: 'center', marginTop: 10}}>{ticket.distribution_start_datetime} - {ticket.distribution_end_datetime}</Text>
          <View style={{flexDirection: 'row', justifyContent: 'center', marginTop: 10, marginBottom: 10}}>
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
            <Text style={{textAlign: 'center'}}> * ${ticket.ticket_price} = ${ticket.ticket_price * this.props.quantity}</Text>
          </View>
        </Animated.View>

        {this.getDeleteButton()}

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
