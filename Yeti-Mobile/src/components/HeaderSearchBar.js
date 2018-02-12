import React from 'react';
import {
  Text,
  View,
  Dimensions,
  Platform,
  TouchableOpacity,
  StyleSheet, TextInput, Button, Image,
} from 'react-native';
import Icon from 'react-native-vector-icons/FontAwesome';


export default class HeaderSearchBar extends React.Component{
  render() {
    return (
      <View style={styles.searchSection}>
        <Icon style={styles.searchIcon} name="search" size={16}/>
        <TextInput
          style={styles.input}
          placeholder={this.props.placeholderText || 'Search'}
          onChangeText={(searchString) => {this.setState({searchString})}}
          underlineColorAndroid="transparent"
        />
      </View>
    )
  }
}

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