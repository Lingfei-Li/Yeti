
import React from 'react'
import {StyleSheet, Button, FlatList, Image, Navigator, Picker, Slider, Text, View, TextInput} from "react-native";
import { getMockTickets } from '../mockingData/ticket'
import log from '../components/log';
import TicketList from "../components/ticket/TicketList";
import TicketListRow from '../components/ticket/TicketListRow'
import LogoTitle from "../components/LogoTitle";

export default class SideMenu extends React.Component {

  getStyle(left=-100) {
    return {
      position: 'absolute',
      flex: 1,
      left: left,
      width: 50,
      height: 200,
      backgroundColor: '#eee',
      alignItems: 'center',
    }
  }

  render() {
      return (
          <View style={this.getStyle(this.props.leftPos)}>
            <Text>WHATATTTATAT!</Text>
          </View>
      )
  }
}


const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    flex: 1,
    width: 100,
    height: 100,
    backgroundColor: '#eee',
    alignItems: 'center',
  },
}) ;
