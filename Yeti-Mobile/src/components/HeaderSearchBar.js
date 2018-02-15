import React from 'react';
import * as Actions from '../actions/index'
import {
  Text,
  View,
  Dimensions,
  Platform,
  TouchableOpacity,
  StyleSheet, TextInput, Button, Image, Picker,
} from 'react-native';
import Icon from 'react-native-vector-icons/FontAwesome';
import {bindActionCreators} from "redux";
import {connect} from "react-redux";


class HeaderSearchBar extends React.Component{
  render() {
    return (
      <View style={styles.searchSection}>
        <Icon style={styles.searchIcon} name="search" size={16}/>
        <TextInput
          style={styles.input}
          placeholder={this.props.placeholderText || 'Search'}
          onChangeText={(text) => {this.props.updateTicketSearchText(text)}}
          underlineColorAndroid="transparent"
          clearButtonMode="unless-editing"
        />
      </View>
    )
  }
}

function mapStateToProps(state) {
  return {
    ticketSearchText: state.ticketSearchText
  }
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators(Actions, dispatch);
}

export default connect(mapStateToProps, mapDispatchToProps)(HeaderSearchBar)

const styles = StyleSheet.create({
  searchSection: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#eee',
    height: 30,
    width: '100%',
    borderRadius: 8,
  },
  searchIcon: {
    paddingLeft: 10,
    paddingRight: 5,
    color: '#bbb',
  },
  input: {
    width: '100%',
    backgroundColor: 'none',
  },
});