import Icon from 'react-native-vector-icons/FontAwesome';
import React from 'react'
import {StyleSheet, Button, Image, Text, TouchableOpacity, View} from "react-native";
import Styles from '../styles'
import HeaderSearchBar from "../components/HeaderSearchBar";
import CommonStyles from '../styles';



export default class ShoppingCart extends React.Component {
  static navigationOptions = ({navigation}) => ({
    headerTitle: <Text style={{fontWeight:'bold', fontSize: 18}}>Shopping Cart</Text>,
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
          onPress={() => navigation.navigate('TicketStack') }
        >
          <Icon name='ticket' size={28} color='#666' style={CommonStyles.headerRightItem}/>
        </TouchableOpacity>
      </View>
    )
  });

  render() {
      return <Text>Your Shopping Cart:</Text>
  }

}

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
}) ;
