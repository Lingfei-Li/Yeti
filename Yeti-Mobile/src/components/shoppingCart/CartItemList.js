import React from 'react';
import {
  Text,
  View,
  Dimensions,
  TouchableOpacity,
  StyleSheet, FlatList,
  Platform, Button,
  ScrollView
} from 'react-native';
import Icon from 'react-native-vector-icons/FontAwesome';
import {bindActionCreators} from "redux";
import {connect} from "react-redux";
import * as Actions from '../../actions/index'
import log from "../log";
import {TICKET_LIST_GROUP_BY_TICKET_TYPE, TICKET_LIST_GROUP_BY_PICKUP_TIME} from '../../reducers/index'
import RowSeparator from '../RowSeparator';
import {Dropdown} from "react-native-material-dropdown";
import CartItemListRow from "./CartItemListRow";
import OrderSummaryBanner from "./OrderSummaryBannerRow";


class CartItemList extends React.Component{

  _keyExtractor = (ticket, index) => ticket.ticketId;

  renderTicketRow = ({item}) => {
    console.log('cart item: ' + JSON.stringify(item));
    return (
      <CartItemListRow ticket={item} quantity={item.purchase_amount}/>
    );
  };

  render() {
    return (
      <View style={styles.cartItemList}>
        <FlatList
          data={this.props.shoppingCart}
          renderItem={this.renderTicketRow}
          keyExtractor={this._keyExtractor}
          ListFooterComponent={(<OrderSummaryBanner navigation={this.props.navigation}/>)}
        />
      </View>
    )
  }
}


function mapStateToProps(state) {
  return {
    shoppingCart: state.shoppingCart,
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
