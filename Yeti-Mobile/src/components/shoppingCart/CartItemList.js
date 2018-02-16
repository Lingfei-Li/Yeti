import React from 'react';
import {
  Text,
  View,
  Dimensions,
  TouchableOpacity,
  StyleSheet, FlatList,
  Platform, Button
} from 'react-native';
import Icon from 'react-native-vector-icons/FontAwesome';
import {bindActionCreators} from "redux";
import {connect} from "react-redux";
import * as Actions from '../../actions/index'
import log from "../log";
import {TICKET_LIST_GROUP_BY_TICKET_TYPE, TICKET_LIST_GROUP_BY_PICKUP_TIME} from '../../reducers/index'
import RowSeparator from '../RowSeparator';


class CartItemList extends React.Component{
  _keyExtractor = (ticket, index) => ticket.ticketId;

  getTicket(singleTicketOrder) {
    return parseFloat(singleTicketOrder.purchaseAmount) * parseFloat(singleTicketOrder.ticket.ticketPrice);
  }

  renderTicketRow = ({item}) => {
    return (
      <View>
        <Text style={{textAlign: 'center', fontWeight: 'bold', fontSize: 20}}>{item.ticket.ticketType}</Text>
        <Text style={{textAlign: 'center'}}>{item.ticket.distributionStartTime} - {item.ticket.distributionStartTime}</Text>
        <Text style={{textAlign: 'center'}}>{item.purchaseAmount} * ${item.ticket.ticketPrice} = ${this.getTicket(item)}</Text>
        <Button title="Delete" onPress={() => {this.props.deleteTicketFromCart(item.ticket.ticketId)}}/>
        <RowSeparator/>
      </View>
    );
  };

  render() {
    return (
      <View style={styles.ticketList}>
        <FlatList
          data={this.props.shoppingCart}
          renderItem={this.renderTicketRow}
          keyExtractor={this._keyExtractor}
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

const isIphoneX = () => {
  let d = Dimensions.get('window');
  const { height, width } = d;
  return (
    // This has to be iOS duh
    Platform.OS === 'ios' &&

    // Accounting for the height in either orientation
    (height === 812 || width === 812)
  );
};

const styles = StyleSheet.create({
  ticketList: {
    flex: 1,
    width: '100%',
    paddingBottom: isIphoneX() ? 55 : 39,
  },
  noResultBanner: {
    width: '100%',
    height: 50,
    fontWeight: 'bold',
    fontSize: 20,
    color: '#ccc',
    textAlign: 'center',
    marginTop: 20,
    fontFamily: Platform.OS === 'ios' ? "Avenir" : "Roboto"
  },
}) ;
