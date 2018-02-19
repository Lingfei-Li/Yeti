import Icon from 'react-native-vector-icons/FontAwesome';
import React from 'react'
import {StyleSheet, Button, Image, Text, TouchableOpacity, View} from "react-native";
import Styles from '../styles'
import HeaderSearchBar from "../components/order/HeaderSearchBar";
import OpenDrawerButton from "../components/headerButton/OpenDrawerButton";
import TicketListButton from "../components/headerButton/TicketListButton";
import OrderItemList from "../components/order/OrderItemList";



export default class MyOrders extends React.Component {
  static navigationOptions = ({navigation}) => ({
    headerStyle: Styles.headerStyle,
    headerTitle: <HeaderSearchBar placeholderText="Search Orders"/>,
    headerLeft: <OpenDrawerButton navigation={navigation}/>,
    headerRight: <TicketListButton navigation={navigation}/>
  });

  render() {
    return (
      <View style={styles.container}>
        <OrderItemList navigation={this.props.navigation}/>
      </View>
    )
  }

}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'white',
    alignItems: 'center',
  },
}) ;
