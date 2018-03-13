import React from 'react'
import {Linking, StyleSheet, Button, FlatList, Image, Navigator, Picker, Slider, Text, View, TextInput, TouchableHighlight, TouchableOpacity} from "react-native";
import { getAllTickets } from '../client/ticket'
import TicketList from "../components/ticket/TicketList";
import HeaderSearchBar from "../components/ticket/HeaderSearchBar";
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
import CommonStyles from '../styles';
import ShoppingCartButton from '../components/headerButton/ShoppingCartButton';
import OpenDrawerButton from '../components/headerButton/OpenDrawerButton';
import PickupNotification from "../components/ticket/PickupNotification";

const { Popover } = renderers;

class HomeScreen extends React.Component {
  static navigationOptions = ({navigation}) => ({
    headerStyle: CommonStyles.headerStyle,
    headerTitle: <HeaderSearchBar placeholderText='Search Tickets e.g. "Stevens Tue"'/>,
    headerLeft: <OpenDrawerButton navigation={navigation}/>,
    headerRight: <ShoppingCartButton navigation={navigation}/>,
  });

  constructor(props) {
    super(props);
    this.state = {
      // Set state variables here
    };
  }

  componentDidMount() {
    getAllTickets().then((response) => {
      const ticketList = JSON.parse(response.data);
      this.props.setOrRefreshTicketList(ticketList);
    }).catch((error) => {
      alert("Failed to get tickets. Please retry or check your internet connection. Error: " + JSON.stringify(error));
    });
  }

  render() {
    return (
      <View style={styles.container}>
        <OptionsBar />

        <TicketList navigation={this.props.navigation}/>

        <PickupNotification navigation={this.props.navigation}/>

      </View>
    )
  }
}


// This function provides access to data in the Redux state in the React component
// In this example, the value of this.props.count will now always have the same value
// As the count value in the Redux state
function mapStateToProps(state) {
  return {
    areYouOkay: state.areYouOkay,
    count: state.count
  }
}

// This function provides a means of sending actions so that data in the Redux store
// can be modified. In this example, calling this.props.addToCounter() will now dispatch
// (send) an action so that the reducer can update the Redux state.
function mapDispatchToProps(dispatch) {
  return bindActionCreators(Actions, dispatch);
}

export default connect(mapStateToProps, mapDispatchToProps)(HomeScreen)


const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
  },
}) ;
