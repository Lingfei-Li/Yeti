import React from 'react'
import {Vibration, Linking, StyleSheet, Button, FlatList, Image, Navigator, Picker, Slider, Text, View, TextInput, TouchableHighlight, TouchableOpacity, ScrollView} from "react-native";
import { getMockTickets } from '../mockingData/ticket'
import TicketList from "../components/ticket/TicketList";
import Icon from 'react-native-vector-icons/FontAwesome';
import {
  Menu,
  MenuProvider,
  MenuOptions,
  MenuTrigger,
  renderers,
} from 'react-native-popup-menu';
import {bindActionCreators} from "redux";
import * as Actions from '../actions/index'
import { connect } from 'react-redux'
import ShoppingCartButton from '../components/headerButton/ShoppingCartButton';
import GoBackButton from '../components/headerButton/GoBackButton';
import {Dropdown} from "react-native-material-dropdown";
import log from "../components/log";
import CommonStyles from "../styles";
import AddToCartConfirmationBanner from "../components/ticketDetails/AddToCartConfirmationBanner";

class TicketDetails extends React.Component {
  static navigationOptions = ({navigation}) => ({
    drawerLockMode: 'locked-closed',
    headerStyle: CommonStyles.headerStyle,
    headerTitle: <Text style={{fontWeight: 'bold', fontSize: 18}}>Ticket Details</Text>,
    headerLeft: <GoBackButton navigation={navigation}/>,
    headerRight: <ShoppingCartButton navigation={navigation}/>,
  });


  constructor(props) {
    super(props);
    this.state = {
      quantity: 1,
      displayConfirmationBanner: false
    };
  }

  confirmationBanner() {
    if(this.state.displayConfirmationBanner) {
      return (<AddToCartConfirmationBanner navigation={this.props.navigation} />);
    }
    return null;
  }


  render() {
    // Use as props
    const { params } = this.props.navigation.state;
    const ticket = params.ticket;

    const purchaseAmountOptions = [
      {value: 1},
      {value: 2},
      {value: 3},
      {value: 4},
      {value: 5},
    ];

    return (
      <View style={styles.container}>

        {this.confirmationBanner()}

        <ScrollView style={{flex: 1, width: '100%'}}>
          <View style={{flex: 1, alignItems: 'center'}}>
            <Text style={{fontSize: 22, marginTop: 10}}>{ticket.ticketType}</Text>
            <Text>{ticket.ticketAmount} tickets left</Text>
            <Text style={{fontSize: 20, fontWeight: 'bold', marginTop: 12, marginBottom: 8}}>$ {ticket.ticketPrice}</Text>

            <Text>{ticket.distributionStartTime} - {ticket.distributionEndTime} (x hours later)</Text>

            <View style={styles.quantityDropdown}>
              <Dropdown
                label="Qty: "
                data={purchaseAmountOptions}
                value={1}
                style={styles.quantityDropdown}
                onChangeText={(value) => {
                  this.setState({quantity: parseInt(value)})
                }}
              />
            </View>

            <Button
              title='Add to cart'
              color='#00699D'
              onPress={() => {
                const quantity = parseInt(this.state.quantity);
                if(quantity !== 0) {
                  this.props.addTicketToCart(ticket, parseInt(quantity));
                  this.setState({displayConfirmationBanner: true});
                  Vibration.vibrate();
                } else {
                  alert('Please choose a purchase quantity');
                }
              }}
            />
          </View>
        </ScrollView>
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

export default connect(mapStateToProps, mapDispatchToProps)(TicketDetails)


const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  quantityDropdown: {
    width: 50,
    marginLeft: 8
  }
}) ;
