/**
 * Created by Yida Yin on 1/4/18
 */

import React from 'react';
import {
  Text,
  View,
  FlatList,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';
import Icon from 'react-native-vector-icons/FontAwesome';

import Header from '../components/Header';
import LambdaAPI from '../LambdaAPI';


const FakeData = [
  {
    name: 'John Doe',
    email: 'john@amazon.com',
    transactions: [
      {
        date: '12/25/2017',
        amount: '59',
        method: 'Venmo',
        notes: '1 Crystal Mountain Ticket',
        confirmed: false,
      },
      {
        date: '12/25/2017',
        amount: '118',
        method: 'Venmo',
        notes: '2 More Crystal Mountain Ticket; 2 More Crystal Mountain Ticket; 2 More Crystal Mountain Ticket; 2 More Crystal Mountain Ticket; 2 More Crystal Mountain Ticket',
        confirmed: false,
      },
      {
        date: '12/14/2017',
        amount: '59',
        method: 'Venmo',
        notes: '1 Stevens Ticket',
        confirmed: true,
      }
    ]
  },
  {
    name: 'Homer Simpson',
    email: 'homer@amazon.com',
    transactions: [
      {
        date: '12/28/2017',
        amount: '59',
        method: 'Venmo',
        notes: '1 Crystal Mountain Ticket',
        confirmed: false,
      },
    ]
  },
  {
    name: 'Tom Jerry',
    email: 'tom@amazon.com',
    transactions: [
      {
        date: '12/28/2017',
        amount: '59',
        method: 'Venmo',
        notes: '1 Crystal Mountain Ticket',
        confirmed: false,
      },
      {
        date: '12/28/2017',
        amount: '59',
        method: 'Venmo',
        notes: '1 Crystal Mountain Ticket',
        confirmed: true,
      },
    ]
  },
];

export default class TransactionListView extends React.Component {
  constructor(props) {
    super(props);
  }

  _renderItem(item) {
    const {name, email, transactions} = item;
    return (
      <TouchableOpacity
        onPress={() => this.props.navigation.navigate('TransactionDetails', {person: item})}
      >
        <View style={{alignItems: 'flex-start', paddingLeft: '6%', paddingRight: '6%', paddingTop: 5, paddingBottom: 5}}>
          <Text style={{fontWeight: 'bold'}}>{name}</Text>
          <Text>{email}</Text>
          <Text>    {transactions.length} Transactions</Text>
        </View>
      </TouchableOpacity>
    )
  }

  _onTyping = (text) => {

  };

  render() {
    return (
      <View style={styles.container}>
        <Header
          title='Transactions'
          rightItem={<Icon name={'gear'} size={26}/>}
        />

        <FlatList
          data={FakeData}
          renderItem={({item}) => this._renderItem(item)}
          keyExtractor={(_, i) => i}

          ItemSeparatorComponent={() => <View style={styles.separator}/>}
          style={{width: '100%', height: '100%'}}
        />
      </View>
    )
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  separator: {
    height: 1,
    width: '100%',
    backgroundColor: '#dddddd'
  },
});