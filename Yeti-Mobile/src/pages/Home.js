import React from 'react'
import {Linking, StyleSheet, Button, FlatList, Image, Navigator, Picker, Slider, Text, View, TextInput, TouchableHighlight, TouchableOpacity} from "react-native";
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
import CommonStyles from '../styles';

const { Popover } = renderers;

class HomeScreen extends React.Component {
  static navigationOptions = ({navigation}) => ({
    headerStyle: {
      backgroundColor: 'white'
    },
    headerTitle: <HeaderSearchBar placeholderText="Search Tickets e.g. Stevens Tue"/>,
    headerLeft: (
      <View style={CommonStyles.headerItemView}>
        <TouchableOpacity
          style={CommonStyles.headerButton}
          onPress={() => navigation.navigate('DrawerOpen') }
        >
          <Icon name='bars' size={28} color='#666' style={CommonStyles.headerLeftItem}/>
        </TouchableOpacity>
      </View>
    ),
    headerRight: (
      <View style={CommonStyles.headerItemView}>
        <TouchableOpacity
        style={CommonStyles.headerButton}
        onPress={() => navigation.navigate('ShoppingCartStack') }
        >
          <Icon name='shopping-cart' size={28} color='#666' style={CommonStyles.headerRightItem}/>
        </TouchableOpacity>
      </View>
    ),
  });


  constructor(props) {
    super(props);
    this.state = {
      // Set state variables here
    };
  }

  componentDidMount() {
    this.props.navigation.setParams({

    });
  }

  render() {
    return (
      <View style={styles.container}>
        <OptionsBar />

        <TicketList tickets={getMockTickets()} navigation={this.props.navigation}/>

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
  menuContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: 10,
    backgroundColor: '#ecf0f1',
  },
  paragraph: {
    margin: 24,
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
    color: '#34495e',
  },
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
  },
  separator: {
    height: 1,
    width: '100%',
    backgroundColor: '#dddddd'
  },
}) ;
