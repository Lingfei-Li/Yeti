import React from 'react';
import {
  Text,
  View,
  Dimensions,
  TouchableOpacity,
  StyleSheet, FlatList,
  Platform, RefreshControl
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
import {getAllTickets} from "../../client/ticket";


class TicketList extends React.Component{

  constructor(props) {
    super(props);
    this.state = {
      refreshingTickets: false
    }
  }

  refreshTickets() {
    this.setState({refreshingTickets: true});
    getAllTickets().then((response) => {
      const ticketList = JSON.parse(response.data);
      this.props.setOrRefreshTicketList(ticketList);
      this.setState({refreshingTickets: false});
    }).catch((error) => {
        this.setState({refreshingTickets: false});
    });
  }

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
    let tickets = JSON.parse(JSON.stringify(this.props.ticketList));
    const rawSearchText = this.props.ticketSearchText;
    const searchTextList = rawSearchText.split(' ');

    return tickets.filter((t) => {
      const searchableValues = [t.ticket_type, t.distribution_start_datetime, t.distribution_end_datetime, t.distribution_location, t.ticket_amount, t.ticket_price];

      // Use 2 reducers to pick tickets that have at least one matching property per search word
      return searchTextList.reduce((accumulatorForTicket, searchText) => {
        const result = searchableValues.reduce((accumulatorForValue, searchableValue) => {
          if(searchableValue === undefined) {
            return accumulatorForValue;
          }
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
        const pickupTime = ticket.distribution_start_datetime + "," + ticket.distribution_end_datetime;
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
        const ticketType = ticket.ticket_type;
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
          refreshControl={
            <RefreshControl
              refreshing={this.state.refreshingTickets}
              onRefresh={this.refreshTickets.bind(this)}
            />
          }
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
    ticketList: state.ticketList,
    ticketListGroupBy: state.ticketListGroupBy,
    ticketSearchText: state.ticketSearchText
  }
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators(Actions, dispatch);
}

export default connect(mapStateToProps, mapDispatchToProps)(TicketList)

const styles = StyleSheet.create({
  ticketList: {
    width: '100%',
    flex: 1,
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
