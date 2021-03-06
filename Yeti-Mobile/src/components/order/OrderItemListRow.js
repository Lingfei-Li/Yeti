import React from 'react';
import QRCode from 'react-native-qrcode'
import moment from 'moment';
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


class OrderItemListRow extends React.Component{

  state = {
  };

  parseOrderPlacedTime(orderPlacedTime) {
    return moment(orderPlacedTime).format('M-D ddd YYYY');
  }

  getTotalTicketsInOrder(order) {
    return order.orderItems.reduce((accumulator, orderItem) => {
      return accumulator + orderItem.purchase_amount;
    }, 0);
  }

  getPaymentStatusString(statusCode) {
    // TODO: The below mapping is not official
    const status = {
      0: 'Not paid',
      1: 'Paid',
      2: 'Partially Paid',
      3: 'Overly Paid',
      4: 'Refund requested',
      5: 'Refund completed',
      6: 'Refund rejected',
    };
    return status[statusCode];
  }

  getPickupStatusString(statusCode) {
    // TODO: The below mapping is not official
    const status = {
      0: 'Not picked up',
      1: 'Picked up',
    };
    return status[statusCode];
  }

  getQrCodeValue(orderId, ticketId) {
    return `${orderId}/${ticketId}`;
  }

  getDynamicTicketContainerStyle(ticket) {
    if(moment(ticket.distribution_start_datetime).isSame(moment(), 'day')) {
      return {
        borderColor: '#00699D',
        shadowColor: '#eee',
        shadowOffset: {
          width: 5,
          height: 5
        },
        shadowOpacity: 0.5
      };
    }
    return {
      borderColor: '#eee'
    };
  }

  getTicketList(order) {
    return order.ticket_list.map((ticket) => {
      return (
        <View style={[styles.ticketContainer, this.getDynamicTicketContainerStyle(ticket)]}>
          <Text style={styles.ticketAttributeText}>{ticket.ticket_type}</Text>
          <Text style={styles.ticketAttributeText}>{ticket.distribution_start_datetime} - {ticket.distribution_end_datetime} (x hours later)</Text>
          <Text style={styles.ticketAttributeText}>{this.getPickupStatusString(ticket.pickupStatus)}</Text>
          <View style={styles.qrCodeView}>
            <QRCode
              value={this.getQrCodeValue(order.orderId, ticket.ticketId)}
              size={100}
              bgColor='#00699D'
              fgColor='white'/>
          </View>
        </View>
      );
    });
  }

  render() {

    const order = this.props.order;

    return (
      <View>
        <Text style={{textAlign: 'left', fontSize: 18, marginTop: 20, marginLeft: 20}}>Order placed: {this.parseOrderPlacedTime(order.orderPlacedTime)}</Text>
        <Text style={{textAlign: 'left', fontSize: 18, marginTop: 20, marginLeft: 20}}>Payment Status: {this.getPaymentStatusString(order.orderPaymentStatus)}</Text>

        {this.getTicketList(order)}

        <RowSeparator/>

      </View>
    )
  }
}


function mapDispatchToProps(dispatch) {
  return bindActionCreators(Actions, dispatch);
}

export default connect(null, mapDispatchToProps)(OrderItemListRow)


const styles = StyleSheet.create({
  ticketContainer: {
    borderColor: '#eee',
    borderWidth: 1,
    borderRadius: 5,
    justifyContent: 'center',
    alignItems: 'center',
    margin: 10,
    padding: 10,
  },
  ticketAttributeText: {
    marginTop: 10,
    marginBottom: 10,
  }
}) ;
