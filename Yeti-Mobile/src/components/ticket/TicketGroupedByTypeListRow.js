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
  render() {
    return (
      <View>
        <View style={styles.ticketRow}>
          <Text style={styles.ticketTitle}>{this.props.ticketGroup.key}</Text>
        </View>
        <RowSeparator />
      </View>
    )
  }
}



const styles = StyleSheet.create({
  ticketRow: {
    height: 100,
    width: '100%',
  },
  ticketTitle: {
    fontWeight: 'bold',
    fontSize: 20,
  },
  ticketAmount: {
  fontSize: 18,
},
  ticketDistributionTime: {
    fontSize: 14,
  },
}) ;
