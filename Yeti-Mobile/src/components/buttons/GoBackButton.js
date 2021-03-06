import * as Actions from '../../actions/index'
import React from 'react'
import {StyleSheet, Button, FlatList, Image, Navigator, Picker, Slider, Text, View, TextInput, TouchableOpacity} from "react-native";
import Icon from 'react-native-vector-icons/FontAwesome';
import {bindActionCreators} from "redux";
import {connect} from "react-redux";
import {TICKET_LIST_GROUP_BY_PICKUP_TIME, TICKET_LIST_GROUP_BY_TICKET_TYPE} from "../../reducers/index";
import CommonStyles from "../../styles";

class GoBackButton extends React.Component {
  render() {
    return (
      <View style={CommonStyles.headerItemView}>
        <TouchableOpacity
          style={CommonStyles.headerButton}
          onPress={() => this.props.navigation.goBack() }
        >
          <Icon name='chevron-left' size={28} color='#666' style={CommonStyles.headerLeftItem}/>
        </TouchableOpacity>
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

export default connect(mapStateToProps, mapDispatchToProps)(GoBackButton)

const styles = StyleSheet.create({
}) ;
