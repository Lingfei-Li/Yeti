import Icon from 'react-native-vector-icons/FontAwesome';
import React from 'react'
import {StyleSheet, Button, Image, Text, TouchableOpacity, View} from "react-native";
import Styles from '../styles'
import HeaderSearchBar from "../components/HeaderSearchBar";



export default class MyOrders extends React.Component {
  static navigationOptions = ({navigation}) => ({
    headerTitle: <HeaderSearchBar placeholderText="Search Orders"/>,
    headerLeft: (
      <View style={styles.headerItemView}>
          <TouchableOpacity
            style={styles.headerButton}
            onPress={() => navigation.navigate('DrawerOpen') }
          >
              <Icon name='bars' size={28} color='#666' style={styles.headerLeftItem}/>
          </TouchableOpacity>
      </View>
    ),
    headerRight: (
      <View style={styles.headerItemView}>
        <TouchableOpacity
          style={styles.headerButton}
          onPress={() => navigation.navigate('TicketStack') }
        >
          <Icon name='ticket' size={28} color='#666' style={styles.headerRightItem}/>
        </TouchableOpacity>
      </View>
    )
  });

  render() {
      return <Text>Your Order History:</Text>
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
  separator: {
    height: 1,
    width: '100%',
    backgroundColor: '#dddddd'
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
    // backgroundColor: '#eee',
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
