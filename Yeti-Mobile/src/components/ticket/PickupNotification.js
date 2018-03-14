import * as Actions from '../../actions/index'
import React from 'react'
import {StyleSheet, Button, FlatList, Image, Navigator, Picker, Slider, Text, View, TextInput, TouchableOpacity} from "react-native";
import Icon from 'react-native-vector-icons/FontAwesome';
import {bindActionCreators} from "redux";
import {connect} from "react-redux";
import {TICKET_LIST_GROUP_BY_PICKUP_TIME, TICKET_LIST_GROUP_BY_TICKET_TYPE} from "../../reducers/index";

class PickupNotification extends React.Component {
  render() {

    return (
      <View style={styles.pickupNotification}>
        <Button
          title='Pick up your tickets today! 🎅 '
          onPress={() => this.props.navigation.navigate('MyOrders')}
          color="#00699D"
        />
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

export default connect(mapStateToProps, mapDispatchToProps)(PickupNotification)

const styles = StyleSheet.create({
  pickupNotification: {
    bottom: 0,
    width: '100%',
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
    borderTopColor: '#ddd',
    borderTopWidth: 1,
    shadowColor: '#eee',
    shadowOffset: {
      width: 0,
      height: -5
    },
    shadowOpacity: 0.5
  },
}) ;
