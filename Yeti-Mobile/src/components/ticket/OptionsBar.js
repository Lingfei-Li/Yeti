import * as Actions from '../../actions/index'
import React from 'react'
import {StyleSheet, Button, FlatList, Image, Navigator, Picker, Slider, Text, View, TextInput, TouchableOpacity} from "react-native";
import Icon from 'react-native-vector-icons/FontAwesome';
import {bindActionCreators} from "redux";
import {connect} from "react-redux";
import {TICKET_LIST_GROUP_BY_PICKUP_TIME, TICKET_LIST_GROUP_BY_TICKET_TYPE} from "../../reducers/index";

class OptionsBar extends React.Component {

  getGroupByElements(groupBy) {
    if(groupBy === TICKET_LIST_GROUP_BY_PICKUP_TIME) {
      return (
        <View style={{flexDirection: 'row'}}>
          <Text
            style={[{marginRight: 5}, this.props.ticketListGroupBy === TICKET_LIST_GROUP_BY_PICKUP_TIME ? styles.highlightedItemText : null]}

          >
            Group By {groupBy}
          </Text>
          <Icon name='calendar' size={14} color='#666'
                style={[this.props.ticketListGroupBy === TICKET_LIST_GROUP_BY_PICKUP_TIME ? styles.highlightedItemIcon : null]}
          />
        </View>
      );
    } else {
      return (
        <View style={{flexDirection: 'row'}}>
          <Text
            // style={[this.props.ticketListGroupBy === TICKET_LIST_GROUP_BY_TICKET_TYPE ? {fontWeight: "bold"} : {fontWeight: 'regular'}]}
            style={[{marginRight: 5}, this.props.ticketListGroupBy === TICKET_LIST_GROUP_BY_TICKET_TYPE ? styles.highlightedItemText : null]}
          >
            Group By {groupBy}
          </Text>
          <Icon name='ticket' size={14} color='#666'
                style={[this.props.ticketListGroupBy === TICKET_LIST_GROUP_BY_TICKET_TYPE ? styles.highlightedItemIcon : null]}
          />
        </View>
      );
    }
  }

  render() {
      return (
          <View style={styles.optionsBar}>
            <TouchableOpacity
              onPress={() => this.props.setTicketListGroupByPickupTime() }
              style={styles.rightItem}
            >
              {this.getGroupByElements(TICKET_LIST_GROUP_BY_PICKUP_TIME)}
            </TouchableOpacity>

            <View style={styles.separator} />

            <TouchableOpacity
              onPress={() => this.props.setTicketListGroupByTicketType() }
              style={styles.leftItem}
            >
              {this.getGroupByElements(TICKET_LIST_GROUP_BY_TICKET_TYPE)}
            </TouchableOpacity>
          </View>
      )
  }
}


function mapStateToProps(state) {
  return {
    ticketListGroupBy: state.ticketListGroupBy
  }
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators(Actions, dispatch);
}

export default connect(mapStateToProps, mapDispatchToProps)(OptionsBar)

const styles = StyleSheet.create({
  optionsBar: {
    width: '100%',
    height: 35,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderBottomColor: '#ddd',
    borderBottomWidth: 1,
  },
  separator: {
    width: 1,
    backgroundColor: '#ddd',
    height: '60%',
  },
  leftItem: {
    width: '50%',
    height: '100%',
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  rightItem: {
    width: '50%',
    height: '100%',
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  highlightedItemText: {
    fontWeight: 'bold',
    color: '#00699D',
  },
  highlightedItemIcon: {
    color: '#00699D',
  },
}) ;
