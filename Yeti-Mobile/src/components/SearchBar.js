import React from 'react';
import {
  Text,
  View,
  Dimensions,
  Platform,
  TouchableOpacity,
  StyleSheet, TextInput, Button,
} from 'react-native';
import Icon from 'react-native-vector-icons/FontAwesome';
import FilterButton from "./FilterButton";


export default class SearchBar extends React.Component{
  render() {
    return (
      <View style={styles.searchBar}>
        <TextInput
          style={styles.textInput}
          placeholder="Type here to Search!"
          onChangeText={(text) => this.setState({text})}
        />
        <FilterButton/>
      </View>
    )
  }
}

const styles = StyleSheet.create({
  searchBar: {
    height: 50,
    width: '100%',
    backgroundColor: '#ddd',
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingTop: 5,
    paddingBottom: 5,
    paddingLeft: 10,
  },
  textInput: {
    height: 40,
    width: '80%',
    backgroundColor: '#fff',
  },
});