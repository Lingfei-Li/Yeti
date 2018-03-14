import Icon from 'react-native-vector-icons/FontAwesome';
import {bindActionCreators} from "redux";
import {connect} from "react-redux";
import * as Actions from '../actions/index'
import React from 'react'
import {StyleSheet, Button, Image, Text, TouchableOpacity, View} from "react-native";
import Styles from '../styles'
import HeaderSearchBar from "../components/order/HeaderSearchBar";
import OpenDrawerButton from "../components/buttons/OpenDrawerButton";
import TicketListButton from "../components/buttons/TicketListButton";
import OrderItemList from "../components/order/OrderItemList";
import { getMockOrders } from '../mockingData/orders'
import {getAllOrdersForUser} from "../client/order";
import HomeButton from "../components/buttons/HomeButton";


class MyOrders extends React.Component {
  static navigationOptions = ({navigation}) => ({
    headerStyle: Styles.headerStyle,
    headerTitle: <HeaderSearchBar placeholderText="Search Orders"/>,
    headerLeft: <HomeButton navigation={navigation}/>,
  });

  componentDidMount() {
    getAllOrdersForUser().then((response) => {
      const orderList = JSON.parse(response.data);
      this.props.setOrRefreshOrderList(orderList);
    }).catch((error) => {
      alert("Failed to get orders for the current user. Please retry or check your internet connection. Error: " + JSON.stringify(error));
    });
  }

  render() {
    return (
      <View style={styles.container}>
        <OrderItemList navigation={this.props.navigation}/>
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

export default connect(mapStateToProps, mapDispatchToProps)(MyOrders)

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'white',
    alignItems: 'center',
  },
}) ;
