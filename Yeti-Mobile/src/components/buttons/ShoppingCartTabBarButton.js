import * as Actions from '../../actions/index'
import React from 'react'
import {Animated, Easing, Platform, StyleSheet, Button, FlatList, Image, Navigator, Picker, Slider, Text, View, TextInput, TouchableOpacity} from "react-native";
import Icon from 'react-native-vector-icons/FontAwesome';
import {bindActionCreators} from "redux";
import {connect} from "react-redux";
import {TICKET_LIST_GROUP_BY_PICKUP_TIME, TICKET_LIST_GROUP_BY_TICKET_TYPE} from "../../reducers/index";
import CommonStyles from "../../styles";

class ShoppingCartButton extends React.Component {

  getTintColor() {
    if(this.props.tintColor) {
      return this.props.tintColor;
    }
    return '#666';
  }

  render() {
    return (
      <View style={CommonStyles.headerItemView}>
        <View style={CommonStyles.headerButton} >
        <Icon name='shopping-cart' size={28} color={this.getTintColor()} style={CommonStyles.headerRightItem}/>
        <Text style={styles.cartItemsCount}>
          {this.props.shoppingCart.length === 0 ? "" : this.props.shoppingCart.length}
        </Text>
        </View>
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

export default connect(mapStateToProps, mapDispatchToProps)(ShoppingCartButton)

const styles = StyleSheet.create({
  cartItemsCount: {
    top: 9,
    fontSize: 10,
    fontWeight: 'bold',
    color: 'white',
    position: 'absolute',
    fontFamily: Platform.OS === 'ios' ? "Avenir" : "Roboto"
  }
}) ;
