import * as Actions from '../../actions/index'
import React from 'react'
import {StyleSheet, Button, FlatList, Image, Navigator, Picker, Slider, Text, View, TextInput, TouchableOpacity} from "react-native";
import Icon from 'react-native-vector-icons/FontAwesome';
import { getMockTickets } from '../../mockingData/ticket'
import log from '../log';
import SearchBar from "../SearchBar";
import TicketList from "./TicketList";
import TicketListRow from './TicketListRow'
import LogoTitle from "../LogoTitle";
import {bindActionCreators} from "redux";
import {connect} from "react-redux";

class OptionsBar extends React.Component {

  render() {
      return (
          <View style={styles.filterMenu}>
            <TouchableOpacity
              onPress={() => this.props.toggleTicketListGroupBy() }
              style={styles.leftItem}
            >
              {getGroupByElements(this.props.ticketListGroupBy)}
            </TouchableOpacity>

            <View style={styles.separator} />

            <TouchableOpacity
              onPress={() => alert('Filter') }
              style={styles.rightItem}
            >
              <Text>Filter</Text>
            </TouchableOpacity>
          </View>
      )
  }
}

function getGroupByElements(groupBy) {
  if(groupBy === 'Pickup Time') {
    return (
      <View style={{flexDirection: 'row'}}>
        <Text>
          Group By: {groupBy}
        </Text>
        <Icon name='calendar' size={14} color='#666'/>
      </View>
    );
  } else {
    return (
      <View style={{flexDirection: 'row'}}>
        <Text>
          Group By: {groupBy}
        </Text>
        <Icon name='ticket' size={14} color='#666'/>
      </View>
    );
  }
}

function mapStateToProps(state) {
  log.info('OptionsBar state: ' + JSON.stringify(state));
  return {
    ticketListGroupBy: state.ticketListGroupBy
  }
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators(Actions, dispatch);
}

export default connect(mapStateToProps, mapDispatchToProps)(OptionsBar)

const styles = StyleSheet.create({
  filterMenu: {
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
  }
}) ;
