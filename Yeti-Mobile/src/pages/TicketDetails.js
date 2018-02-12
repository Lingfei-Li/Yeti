import React from 'react'
import {Linking, StyleSheet, Button, FlatList, Image, Navigator, Picker, Slider, Text, View, TextInput, TouchableHighlight, TouchableOpacity, ScrollView} from "react-native";
import { getMockTickets } from '../mockingData/ticket'
import SearchBar from "../components/SearchBar";
import TicketList from "../components/ticket/TicketList";
import Icon from 'react-native-vector-icons/FontAwesome';
import HeaderSearchBar from "../components/HeaderSearchBar";
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
import OptionsBar from "../components/ticket/OptionsBar";
import log from "../components/log";

const { Popover } = renderers;

class TicketDetails extends React.Component {
  static navigationOptions = ({navigation}) => ({
    drawerLockMode: 'locked-closed',
    headerStyle: {
      backgroundColor: 'white'
    },
    headerTitle: <HeaderSearchBar placeholderText="Search Ski Tickets" />,
    headerLeft: (
      <View style={styles.headerItemView}>
        <TouchableOpacity
          style={styles.headerButton}
          onPress={() => navigation.goBack() }
        >
          <Icon name='chevron-left' size={28} color='#666' style={styles.headerLeftItem}/>
        </TouchableOpacity>
      </View>
    ),
    headerRight: (
      <View style={styles.headerItemView}>
        <TouchableOpacity
        style={styles.headerButton}
        onPress={() => navigation.navigate('MyOrdersStack') }
        >
          <Icon name='history' size={28} color='#666' style={styles.headerRightItem}/>
        </TouchableOpacity>
      </View>
    ),
  });


  constructor(props) {
    super(props);
    this.state = {
      purchaseAmountText: 0
    };
  }

  componentDidMount() {
    this.props.navigation.setParams({

    });
  }


  render() {
    // Use as props
    const { params } = this.props.navigation.state;
    const ticket = params.ticket;

    const orderId = 'YetiOrder#12345678901234567890#';

    return (
      <View style={styles.container}>
        <ScrollView style={{flex: 1, width: '100%'}}>
          <View style={{flex: 1, alignItems: 'center'}}>
            <Text style={{fontSize: 22, marginTop: 10}}>{ticket.ticketType}</Text>
            <Text>{ticket.ticketAmount} tickets left</Text>
            <Text style={{fontSize: 20, fontWeight: 'bold', marginTop: 12, marginBottom: 8}}>$ {ticket.ticketPrice}</Text>

            <Text>{ticket.distributionStartTime} - {ticket.distributionEndTime} (x hours later)</Text>

            <View style={{flexDirection: 'row', justifyContent: 'center', alignItems: 'center'}} >
              <Text>Purchase Amount: </Text>
              <TextInput
                style={{width: 30, height: 20, borderColor: 'gray', borderWidth: 1, borderRadius: 2}}
                keyboardType='numeric'
                onChangeText={(purchaseAmountText) => this.setState({purchaseAmountText})}
                value={this.state.purchaseAmountText}
              />
            </View>

            <Button
              title='Place Order'
              onPress={() => this.props.navigation.navigate('PaymentPage', {ticket, orderId})}
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
  headerItemView: {
    flex: 1,
    width: 70,
  },
  headerButton: {
    width: '100%',
    height: '100%',
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerLeftItem: {
    width: 28,
    height: 28,
  },
  headerRightItem: {
    width: 28,
    height: 28,
  }

}) ;