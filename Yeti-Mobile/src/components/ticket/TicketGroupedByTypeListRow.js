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
import TicketMetadata from "./TicketMetadata";


export default class TicketGroupedByTypeListRow extends React.Component{

  getTicketDetailsButton(tickets) {
    let details = [];
    tickets.forEach((ticket) => {

      const pickupStartTime = moment(ticket.distribution_start_datetime);
      const pickupEndTime = moment(ticket.distribution_end_datetime);
      const today = moment();
      let dynamicDayOfWeek = '';
      if(pickupStartTime.isSame(today, "day")) {
        dynamicDayOfWeek = 'Today';
      } else if(pickupStartTime.isSame(today, "week")) {
        dynamicDayOfWeek = "This " + pickupStartTime.format("dddd");
      } else {
        dynamicDayOfWeek = pickupStartTime.format("dddd");
      }


      let pickupDateTimeRange = '';
      if(pickupStartTime.year() === pickupEndTime.year() && pickupStartTime.dayOfYear() === pickupEndTime.dayOfYear()) {
        pickupDateTimeRange = (
          <View>
            <Text style={styles.ticketTitle}>{pickupStartTime.format("M-D")} {dynamicDayOfWeek}</Text>
            <Text style={styles.ticketTitle}>{pickupStartTime.format("h:mm")} - {pickupEndTime.format("h:mm a")}</Text>
          </View>
        )
      } else {
        pickupDateTimeRange = (<Text style={styles.ticketTitle}>{pickupStartTime.format("M/D h:mm a")} - {pickupEndTime.format("M/D h:mm a")}</Text>)
      }

      details.push(
        <TouchableOpacity
          onPress={() => this.props.navigation.navigate('TicketDetails', {ticket}) }
          style={styles.ticketDetailsLink}
        >
          {pickupDateTimeRange}
          <TicketMetadata ticket={ticket}/>
        </TouchableOpacity>
      )
    });
    return details;
  }

  render() {
    return (
      <View style={{alignItems: 'center'}}>
        <Text style={styles.ticketGroupTitle}>{this.props.ticketGroup.key}</Text>
        {this.getTicketDetailsButton(this.props.ticketGroup.val)}
        <RowSeparator />
      </View>
    )
  }
}


const styles = StyleSheet.create({
  ticketGroupTitle: {
    fontWeight: 'bold',
    fontSize: 20,
    textAlign: 'center',
    marginTop: 20
  },
  ticketTitle: {
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
    color: '#b00'
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
    shadowColor: '#ccc',
    shadowOffset: {
      width: 0,
      height: 0,
    },
    shadowOpacity: 0.5
  },
}) ;
