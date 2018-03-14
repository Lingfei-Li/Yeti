import React from 'react';
import moment from "moment";
import {
  Text,
  View,
  Dimensions,
  Platform,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';
import Icon from 'react-native-vector-icons/FontAwesome';
import RowSeparator from "../RowSeparator";
import {connect} from "react-redux";
import {bindActionCreators} from "redux";
import * as Actions from '../../actions/index'


export default class TicketMetadata extends React.Component{

  getTicketsLeftTextColor(ticket) {
    if(ticket.ticket_amount < 5) {
      return '#b00';
    } else if (ticket.ticket_amount < 10) {
      return '#b80';
    } else {
      return '#060';
    }
  }

  render() {
    const ticket = this.props.ticket;
    return (
      <View>
        <Text style={[styles.ticketAmountText, {color: this.getTicketsLeftTextColor(ticket)}]}>{ticket.ticket_amount} tickets left</Text>
        <View>
          <Text style={{textAlign: 'center'}}>
            Price: <Text style={styles.ticketPriceText}>${ticket.ticket_price}</Text>
          </Text>
        </View>
        <Text style={{textAlign: 'center'}}>Review: 4.5</Text>
      </View>
    )
  }
}


const styles = StyleSheet.create({
  ticketTitle: {
    fontWeight: 'bold',
    fontSize: 20,
    textAlign: 'center',
    marginTop: 20
  },
  ticketPickupText: {
    fontWeight: 'bold',
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 5
  },
  ticketAmountText: {
    fontSize: 16,
    textAlign: 'center',
    marginTop: 5
  },
  ticketPriceText: {
    fontSize: 16,
    textAlign: 'center',
    marginTop: 5,
    color: '#00669D'
  },
  ticketDetailsLink: {
    fontSize: 14,
    marginTop: 15,
    marginBottom: 15,
    justifyContent: 'center',
    borderWidth: 1,
    width: '80%',
    borderRadius: 10,
    borderColor: '#eee',
    padding: 20,
  },
}) ;
