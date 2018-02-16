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
import RowSeparator from '../RowSeparator';
import {connect} from "react-redux";
import {bindActionCreators} from "redux";
import * as Actions from '../../actions/index'


class TicketListRowComponent extends React.Component{
  render() {
    return (
      <View>
        <View style={styles.ticketRow}>
          <Text>Item!</Text>
        </View>
        <RowSeparator />
      </View>
    )
  }
}


function mapStateToProps(state) {
  return {
  }
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators(Actions, dispatch);
}

export default connect(mapStateToProps, mapDispatchToProps)(TicketListRowComponent)

const styles = StyleSheet.create({
  ticketRow: {
    height: 100,
    width: '100%',
  },
  ticketTitle: {
    fontWeight: 'bold',
    fontSize: 20,
  },
  ticketDistributionTime: {
    fontSize: 14,
  },
  ticketAmount: {
  fontSize: 18,
},
}) ;
