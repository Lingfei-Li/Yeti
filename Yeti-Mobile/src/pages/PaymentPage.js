import React from 'react'
import {Animated, Easing, Dimensions, Clipboard, Linking, StyleSheet, Button, FlatList, Navigator, Picker, Slider, Text, View, TextInput, TouchableHighlight, TouchableOpacity, ScrollView} from "react-native";
import Image from 'react-native-scalable-image';
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
      displayStep2View: false,
      displayStep3View: false,
      displayStep4View: false,
    };
  }

  showStepX(stepX) {
    switch(stepX) {
      case 2:
        this.setState({
          displayStep2View: true
        });
        this._scrollView.scrollTo({x: Dimensions.get('window').width});
        break;
      case 3:
        this.setState({
          displayStep3View: true
        });
        // this._scrollView.scrollTo({x: Dimensions.get('window').width*2});
        setTimeout(() => {this._scrollView.scrollTo({x: Dimensions.get('window').width*2}) }, 1000);
        Linking.openURL('https://venmo.com/code?user_id=1990244970790912928');
        break;
      case 4:
        this.setState({
          displayStep4View: true
        });
        // this._scrollView.scrollTo({x: Dimensions.get('window').width*3});
        setTimeout(() => {this._scrollView.scrollTo({x: Dimensions.get('window').width*2}) }, 1000);
        Linking.openURL('https://venmo.com/code?user_id=1990244970790912928');
        break;
    }
  }

  getTotalPrice(payingOrder) {
    return payingOrder.reduce((accumulator, singleTicketOrder) => {
      return accumulator + parseFloat(singleTicketOrder.purchaseAmount) * parseFloat(singleTicketOrder.ticket.ticketPrice);
    }, 0);
  }

  getPriceForSingleTicketOrder(singleTicketOrder) {
    return parseFloat(singleTicketOrder.purchaseAmount) * parseFloat(singleTicketOrder.ticket.ticketPrice);
  }

  step1View(orderId, payingOrder) {
    const ticketsTextElements = payingOrder.map((singleTicketOrder) => {
        return <Text>{singleTicketOrder.ticket.ticketType} {singleTicketOrder.purchaseAmount} * {singleTicketOrder.ticket.ticketPrice} = ${this.getPriceForSingleTicketOrder(singleTicketOrder)}</Text>
    });

    return (
      <View style={styles.paymentStepView}>
        <Text style={{fontWeight: 'bold', fontSize: 20}}>Pay for your order:</Text>
        {ticketsTextElements}
        <Text>Total: ${this.getTotalPrice(payingOrder)}</Text>
        <Text style={{fontWeight: 'bold', fontSize: 20}}>Click to copy the Order Id</Text>
        <Button
          title={orderId}
          onPress={() => { Clipboard.setString(orderId); this.showStepX(2); this._scrollView.scrollTo({x: Dimensions.get('window').width}) }}
        />
      </View>
    );
  }

  step2View(payingOrder) {
    if(this.state.displayStep2View) {
      return (
        <View style={styles.paymentStepView}>
          <Text style={{fontWeight: 'bold', fontSize: 20}}>Pay ${this.getTotalPrice(payingOrder)} in Venmo</Text>
          <Text style={{fontWeight: 'bold', fontSize: 20}}>Paste the order id in the message</Text>
          <View style={{borderWidth: 1, borderColor: '#eee', margin: 30}}>
            <Image
              source={require('../resources/assets/venmo_payment_demo.gif')}
              width={Dimensions.get('window').width * 0.6}
            />
          </View>
          <TouchableOpacity
            style={styles.openVenmoButton}
            onPress={() => this.showStepX(3)}
          >
            <Text style={styles.openVenmoText}>Open </Text>
            <Image
              source={require('../resources/assets/venmo.png')}
              height={30}
            />
          </TouchableOpacity>
        </View>
      );
    }
    return null;
  }

  step3View() {
    if(this.state.displayStep3View) {
      return (
        <View style={styles.paymentStepView}>
          <Text style={{fontWeight: 'bold', fontSize: 20}}>You're all set!</Text>
          <Text style={{fontWeight: 'bold', fontSize: 20}}>We'll send a confirmation to {this.props.userId}@amazon.com</Text>
          <Button
            style={{bottom: 20}}
            title="Forgot to add Order ID?"
            onPress={() => {this.showStepX(4)}}
          />
        </View>
      )
    }
    return null;
  }

  step4View() {
    if(this.state.displayStep4View) {
      return (
        <View style={styles.paymentStepView}>
          <Text style={{fontWeight: 'bold', fontSize: 20}}>Comment on your payment</Text>
          <Text style={{fontWeight: 'bold', fontSize: 20}}>Add the Order Id</Text>
          <View style={{borderWidth: 1, borderColor: '#eee', margin: 30}}>
            <Image
              source={require('../resources/assets/venmo_add_comment_demo.gif')}
              width={Dimensions.get('window').width * 0.6}
            />
          </View>
          <TouchableOpacity
            style={styles.openVenmoButton}
            onPress={() => this.showStepX(3)}
          >
          <Text style={styles.openVenmoText}>Open </Text>
          <Image
            source={require('../resources/assets/venmo.png')}
            height={30}
          />
          </TouchableOpacity>
        </View>
      )
    }
    return null;
  }


  render() {
    // Use as props
    const { params } = this.props.navigation.state;

    return (
      <View>
        <ScrollView
          ref={(scrollView) => { this._scrollView = scrollView; }}
          style={styles.paymentScrollView}
          pagingEnabled={true}
          horizontal={true}
          showsHorizontalScrollIndicator={false}
        >

          {this.step1View(params.orderId, params.payingOrder)}

          {this.step2View(params.payingOrder)}

          {this.step3View()}

          {this.step4View()}
        </ScrollView>
        <View style={styles.paymentPageFooter}>
          <Button
            title="Close"
            onPress={() => this.props.navigation.goBack()}
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
  openVenmoButton: {
    marginTop: 30,
    flexDirection:'row',
    justifyContent: 'center',
    alignItems: 'center'
  },
  openVenmoText: {
    fontSize: '20',
    fontWeight: 'bold',
    color: '#00699D',
  },
  venmoIcon: {
    width: 60,
  },
  paymentScrollView: {
    width: '100%',
    height: "90%",
    backgroundColor: 'white',
    flexDirection: 'row',
  },
  paymentPageFooter: {
    width: Dimensions.get('window').width,
    height: '10%',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: 'white',
  },
  paymentStepView: {
    width: Dimensions.get('window').width,
    height: '90%',
    justifyContent: 'center',
    alignItems: 'center',
    // borderWidth: 1,
  },
}) ;
