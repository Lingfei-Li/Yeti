import React from 'react'
import {Dimensions, Clipboard, Linking, StyleSheet, Button, FlatList, Navigator, Picker, Slider, Text, View, TextInput, TouchableHighlight, TouchableOpacity, ScrollView} from "react-native";
import Image from 'react-native-scalable-image';
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

class PaymentPage extends React.Component {
  static navigationOptions = ({navigation}) => ({
    drawerLockMode: 'locked-closed',
    headerStyle: {
      backgroundColor: 'white'
    },
    headerTitle: <Text style={{fontWeight: 'bold'}}>Pay your order</Text>,
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

    return (
      <View style={styles.container}>
        <View style={styles.step1View}>
          <Text style={{fontWeight: 'bold', fontSize: 20}}>1. Copy the Order Id</Text>
          <Button
            title={params.orderId}
            onPress={() => Clipboard.setString(params.orderId)}
          />
        </View>

        <View style={styles.step2View}>
          <Text style={{fontWeight: 'bold', fontSize: 20}}>2. Paste in the payment message</Text>
          <View style={{borderWidth: 1, borderColor: '#eee'}}>
            <Image
              source={require('../resources/assets/venmo_payment_page.png')}
              width={Dimensions.get('window').width * 0.8}
            />
          </View>
          <Button
            title="Pay via Venmo"
            onPress={() => Linking.openURL('https://venmo.com/code?user_id=1990244970790912928')}
          />
        </View>


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

export default connect(mapStateToProps, mapDispatchToProps)(PaymentPage)


const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
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
  },
  venmoProfileImage: {
    width: '50%',
    height: '50%',
  },
  venmoPaymentImage: {
    height: '20%',
  },
  step1View: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  step2View: {
    justifyContent: 'center',
    alignItems: 'center',
  }
}) ;
