
import React from 'react'
import {StyleSheet, Button, FlatList, Image, Navigator, Picker, Slider, Text, View, TextInput} from "react-native";
import log from '../log';
import TicketList from "./TicketList";
import TicketListRow from './TicketListRow'
import LogoTitle from "../LogoTitle";

export default class FilterMenu extends React.Component {

  render() {
      return (
          <View style={styles.filterMenu}>
            <Text>WHATATTTATAT!</Text>
          </View>
      )
  }
}

const styles = StyleSheet.create({
  filterMenu: {
    position: 'absolute',
    flex: 1,
    right: 0,
    width: 200,
    height: 1000,
    backgroundColor: '#eee',
    alignItems: 'center',
  }
}) ;
