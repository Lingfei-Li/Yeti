import React from 'react';
import * as Actions from '../../actions/index'
import {
  TouchableWithoutFeedback,
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
        <TouchableOpacity //Expand touchable area to improve UX
          activeOpacity={1}
          onPress={() => {this.SearchTextInput.focus()}}
          style={styles.touchableArea}
        >
          <Icon style={styles.searchIcon} name="search" size={16}/>
          <TextInput
            ref={(element) => this.SearchTextInput = element}
            style={styles.input}
            placeholder={this.props.placeholderText || 'Search'}
            onChangeText={(text) => {this.props.updateTicketSearchText(text)}}
            underlineColorAndroid="transparent"
            clearButtonMode="while-editing"
            blurOnSubmit={true}
            value={this.props.ticketSearchText}
          />
        </TouchableOpacity>
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
  touchableArea: {
    height: '100%',
    width: '100%',
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 8,
  },
  searchIcon: {
    paddingLeft: 10,
    paddingRight: 5,
    color: '#bbb',
  },
  input: {
    flex: '1',
    width: '100%',
  },
});