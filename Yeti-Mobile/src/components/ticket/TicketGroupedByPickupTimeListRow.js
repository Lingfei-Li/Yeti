import React from 'react';
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
import moment from "moment";


export default class TicketGroupedByPickupTimeListRow extends React.Component{

  getTicketDetailsButtonList(tickets) {
    let details = [];
    tickets.forEach((ticket) => {
      details.push(
        <TouchableOpacity
          onPress={() => this.props.navigation.navigate('TicketDetails', {ticket}) }
          style={styles.ticketDetailsLink}
        >
          <Text style={{textAlign: 'center'}}>{ticket.ticket_type} {ticket.ticket_amount} ${ticket.ticket_price}</Text>
        </TouchableOpacity>
      )
    });
    return details;
  }

  getTicketTitle() {
    const pickupTimeRange = this.props.ticketGroup.key.split(',');
    const pickupStartTime = moment(pickupTimeRange[0]);
    const pickupEndTime = moment(pickupTimeRange[1]);
    const today = moment();
    let dynamicDayOfWeek = '';
    if(pickupStartTime.isSame(today, "day")) {
      dynamicDayOfWeek = 'Today';
    }
    else if(pickupStartTime.isSame(today, "week")) {
      dynamicDayOfWeek = "This " + pickupStartTime.format("dddd");
    } else {
      dynamicDayOfWeek = pickupStartTime.format("dddd");
    }
    if(pickupStartTime.year() === pickupEndTime.year() && pickupStartTime.dayOfYear() === pickupEndTime.dayOfYear()) {
      return (
        <View>
          <Text style={styles.ticketTitle}>{pickupStartTime.format("M-D")} {dynamicDayOfWeek}</Text>
          <Text style={styles.ticketTitle}>{pickupStartTime.format("h:mm")} - {pickupEndTime.format("h:mm a")}</Text>
        </View>
      )
    }
    return (
      <Text style={styles.ticketTitle}>{pickupStartTime.format("M/D h:mm a")} - {pickupEndTime.format("M/D h:mm a")}</Text>
    )
  }

  render() {
    return (
      <View style={{alignItems: 'center'}}>
        {this.getTicketTitle()}
        {this.getTicketDetailsButtonList(this.props.ticketGroup.val)}
        <RowSeparator />
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
