import React from 'react';
import {
  Text,
  View,
  Dimensions,
  TouchableOpacity,
  StyleSheet, FlatList,
  Platform, Button,
  ScrollView, RefreshControl
} from 'react-native';
import Icon from 'react-native-vector-icons/FontAwesome';
import {bindActionCreators} from "redux";
import {connect} from "react-redux";
import * as Actions from '../../actions/index'
import log from "../log";
import {TICKET_LIST_GROUP_BY_TICKET_TYPE, TICKET_LIST_GROUP_BY_PICKUP_TIME} from '../../reducers/index'
import RowSeparator from '../RowSeparator';
import {Dropdown} from "react-native-material-dropdown";
import OrderItemListRow from "./OrderItemListRow";
import {getAllOrdersForUser} from "../../client/order";


class CartItemList extends React.Component{

  constructor(props) {
    super(props);
    this.state = {
      refreshingOrders: false
    };
  }

  refreshOrders() {
    this.setState({refreshingOrders: true});
    getAllOrdersForUser().then((response) => {
      const orderList = JSON.parse(response.data);
      this.props.setOrRefreshOrderList(orderList);
      this.setState({refreshingOrders: false});
    }).catch((error) => {
      alert("Failed to refresh order list. Error: " + JSON.stringify(error));
      this.setState({refreshingOrders: false});
    });
  }

  _keyExtractor = (ticket, index) => ticket.ticketId;

  renderTicketRow = ({item}) => {
    return (
      <OrderItemListRow order={item} />
    );
  };

  render() {
    return (
      <View style={styles.cartItemList}>
        <FlatList
          refreshControl={
            <RefreshControl
              refreshing={this.state.refreshingOrders}
              onRefresh={this.refreshOrders.bind(this)}
            />
          }
          data={this.props.orderList}
          renderItem={this.renderTicketRow}
          keyExtractor={this._keyExtractor}
        />
      </View>
    )
  }
}


function mapStateToProps(state) {
  return {
    orderList: state.orderList,
  }
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators(Actions, dispatch);
}

export default connect(mapStateToProps, mapDispatchToProps)(CartItemList)

const styles = StyleSheet.create({
  cartItemList: {
    width: '100%',
    height: '100%',
  },
  quantityDropdown: {
    width: 50,
    marginLeft: 8
  }
}) ;
