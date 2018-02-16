import React from 'react';
import {
  Text,
  View,
  Dimensions,
  TouchableOpacity,
  StyleSheet, FlatList,
  Platform
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
    if(item.noResult === true) {
      return (<Text style={styles.noResultBanner}>No Result</Text>);
    }
    if(this.props.ticketListGroupBy === TICKET_LIST_GROUP_BY_PICKUP_TIME) {
      return (<TicketGroupedByPickupTimeListRow ticketGroup={item} navigation={this.props.navigation}/>);
    } else {
      return (<TicketGroupedByTypeListRow ticketGroup={item} navigation={this.props.navigation}/>);
    }
  };

  getTicketsWithSearchText() {
    let tickets = JSON.parse(JSON.stringify(this.props.tickets));
    const rawSearchText = this.props.ticketSearchText;
    const searchTextList = rawSearchText.split(' ');

    return tickets.filter((t) => {
      const searchableValues = [t.ticketType, t.distributionStartTime, t.distributionEndTime, t.ticketAmount, t.ticketPrice];

      // Use 2 reducers to pick tickets that have at least one matching property per search word
      return searchTextList.reduce((accumulatorForTicket, searchText) => {
        const result = searchableValues.reduce((accumulatorForValue, searchableValue) => {
          return accumulatorForValue || searchableValue.toString().toLowerCase().includes(searchText.toLowerCase());
        }, false);
        return accumulatorForTicket && result;
      }, true);
    });
  }

  getGroupedTickets(tickets, groupBy) {
    if(!tickets || !tickets.length) {
      log.info('No ticket satisfies the search criteria');
      // Return a single-item array so that the FlatList can render a "No Result" banner
      return [{noResult: true}];
    }
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


  render() {
    return (
      <View style={styles.ticketList}>
        <FlatList
          data={this.getGroupedTickets(this.getTicketsWithSearchText(), this.props.ticketListGroupBy)}
          renderItem={this.renderTicketRow}
          keyExtractor={this._keyExtractor}
        />
      </View>
    )
  }
}


function mapStateToProps(state) {
  return {
    ticketListGroupBy: state.ticketListGroupBy,
    ticketSearchText: state.ticketSearchText
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
    height: '100%',
    paddingBottom: isIphoneX() ? 55 : 39,
  },
  noResultBanner: {
    width: '100%',
    height: 50,
    fontWeight: 'bold',
    fontSize: 20,
    color: '#ccc',
    textAlign: 'center',
    marginTop: 20,
    fontFamily: Platform.OS === 'ios' ? "Avenir" : "Roboto"
  },
}) ;
