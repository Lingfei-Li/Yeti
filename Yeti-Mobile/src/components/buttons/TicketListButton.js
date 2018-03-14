import * as Actions from '../../actions/index'
import React from 'react'
import {Animated, Easing, Platform, StyleSheet, Button, FlatList, Image, Navigator, Picker, Slider, Text, View, TextInput, TouchableOpacity} from "react-native";
import Icon from 'react-native-vector-icons/FontAwesome';
import {bindActionCreators} from "redux";
import {connect} from "react-redux";
import {TICKET_LIST_GROUP_BY_PICKUP_TIME, TICKET_LIST_GROUP_BY_TICKET_TYPE} from "../../reducers/index";
import CommonStyles from "../../styles";

class TicketListButton extends React.Component {

  render() {
    return (
      <View style={CommonStyles.headerItemView}>
        <TouchableOpacity
          style={CommonStyles.headerButton}
          onPress={() => this.props.navigation.navigate('Tickets') }
        >

          <Icon name='ticket' size={28} color='#666' style={CommonStyles.headerRightItem}/>
        </TouchableOpacity>
      </View>
    )
  }
}


function mapStateToProps(state) {
  return {
    shoppingCart: state.shoppingCart,
  }
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators(Actions, dispatch);
}

export default connect(mapStateToProps, mapDispatchToProps)(TicketListButton)

const styles = StyleSheet.create({
}) ;
