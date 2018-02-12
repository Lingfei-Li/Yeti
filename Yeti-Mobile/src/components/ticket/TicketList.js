import React from 'react';
import {
  Text,
  View,
  Dimensions,
  Platform,
  TouchableOpacity,
  StyleSheet, FlatList,
} from 'react-native';
import Icon from 'react-native-vector-icons/FontAwesome';
import TicketListRow from "./TicketListRow";
import {bindActionCreators} from "redux";
import {connect} from "react-redux";
import * as Actions from '../../actions/index'
import log from "../log";
import TicketGroupedByPickupTimeListRow from "./TicketGroupedByPickupTimeListRow";
import TicketGroupedByTypeListRow from "./TicketGroupedByTypeListRow";
import {TICKET_LIST_GROUP_BY_TICKET_TYPE, TICKET_LIST_GROUP_BY_PICKUP_TIME} from '../../reducers/index'


class TicketList extends React.Component{
  _keyExtractor = (ticket, index) => ticket.ticketId;

  renderTicketRow = ({item}) => {
    if(this.props.ticketListGroupBy === TICKET_LIST_GROUP_BY_PICKUP_TIME) {
      log.info("TicketList.Group by pickup time item");
      return (<TicketGroupedByPickupTimeListRow ticketGroup={item} navigation={this.props.navigation}/>);
    } else {
      log.info("TicketList.Group by type list row");
      return (<TicketGroupedByTypeListRow ticketGroup={item} navigation={this.props.navigation}/>);
    }
  };

  render() {
    return (
      <View style={styles.ticketList}>
        <FlatList
          data={getGroupedTickets(this.props.tickets, this.props.ticketListGroupBy)}
          renderItem={this.renderTicketRow}
          keyExtractor={this._keyExtractor}
        />
      </View>
    )
  }
}

function getGroupedTickets(tickets, groupBy) {
  log.info("TicketList.getGroupedTickets");
  let groupedTickets = {};
  let groupedTicketsList = [];
  if(groupBy === TICKET_LIST_GROUP_BY_PICKUP_TIME) {
    tickets.forEach((ticket) => {
      const pickupTime = ticket.distributionStartTime + " - " + ticket.distributionEndTime;
      if (!(pickupTime in groupedTickets)) {
        groupedTickets[pickupTime] = [];
      }
      groupedTickets[pickupTime].push(ticket);
    });

    // Transform into FlatList data format
    for(let pickupTime in groupedTickets) if(groupedTickets.hasOwnProperty(pickupTime)) {
      groupedTicketsList.push({
        key: pickupTime,
        val: groupedTickets[pickupTime]
      });
    }
  } else {
    tickets.forEach((ticket) => {
      const ticketType = ticket.ticketType;
      if (!(ticketType in groupedTickets)) {
        groupedTickets[ticketType] = [];
      }
      groupedTickets[ticketType].push(ticket);
    });

    // Transform into FlatList data format
    for(let ticketType in groupedTickets) if(groupedTickets.hasOwnProperty(ticketType)) {
      groupedTicketsList.push({
        key: ticketType,
        val: groupedTickets[ticketType]
      });
    }
  }
  return groupedTicketsList;
}


function mapStateToProps(state) {
  return {
    ticketListGroupBy: state.ticketListGroupBy
  }
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators(Actions, dispatch);
}

export default connect(mapStateToProps, mapDispatchToProps)(TicketList)

const isIphoneX = () => {
  let d = Dimensions.get('window');
  const { height, width } = d;
  return (
    // This has to be iOS duh
    Platform.OS === 'ios' &&

    // Accounting for the height in either orientation
    (height === 812 || width === 812)
  );
};

const styles = StyleSheet.create({
  ticketList: {
    width: '100%',
    paddingBottom: isIphoneX() ? 55 : 39,
  },
}) ;
