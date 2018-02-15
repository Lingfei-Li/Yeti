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
import RowSeparator from "./RowSeparator";
import {connect} from "react-redux";
import {bindActionCreators} from "redux";
import * as Actions from '../../actions/index'


export default class TicketGroupedByTypeListRow extends React.Component{

  getTicketDetailsButton(tickets) {
    let details = [];
    tickets.forEach((ticket) => {
      details.push(
        <TouchableOpacity
          onPress={() => this.props.navigation.navigate('TicketDetails', {ticket}) }
          style={styles.ticketDetailsLink}
        >
          <Text>{ticket.distributionStartTime} - {ticket.distributionStartTime} </Text>
          <Text>{ticket.ticketAmount} ${ticket.ticketPrice}</Text>
        </TouchableOpacity>
      )
    });
    return details;
  }

  render() {
    return (
      <View>
        <Text style={styles.ticketTitle}>{this.props.ticketGroup.key}</Text>
        {this.getTicketDetailsButton(this.props.ticketGroup.val)}
        <RowSeparator />
      </View>
    )
  }
}


const styles = StyleSheet.create({
  ticketTitle: {
    fontWeight: 'bold',
    fontSize: 20,
  },
  ticketDetailsLink: {
    fontSize: 14,
    marginTop: 15,
    marginBottom: 15,
    justifyContent: 'center',
  },
}) ;
