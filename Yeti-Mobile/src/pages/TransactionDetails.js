/**
 * Created by Yida Yin on 1/5/18
 */

import React from 'react';
import {
  Text,
  View,
  FlatList,
  TouchableOpacity,
  Alert,
  StyleSheet,
} from 'react-native';
import Icon from 'react-native-vector-icons/Entypo';

import Header from '../components/Header';
import LambdaAPI from '../LambdaAPI';


export default class TransactionDetails extends React.Component {
  constructor(props) {
    super(props);
  }

  _renderItem(item) {
    const {date, amount, method, notes, confirmed} = item;
    return (
      <TouchableOpacity>
        <View
          style={{
            flex: 1,
            alignItems: 'flex-start',
            marginLeft: '6%',
            marginRight: '6%',
            paddingTop: 5,
            paddingBottom: 5
          }}
        >

          <Text style={{fontWeight: 'bold', fontSize: 20}}>{date}</Text>
          <Text style={{fontWeight: 'bold', fontSize: 15, color: 'green'}}>{confirmed ? "Confirmed" : ""}</Text>

          <View style={{flexDirection: 'row'}}>
            <Text style={{fontWeight: 'bold'}}>Amount: </Text>
            <Text>${amount}</Text>
          </View>
          <View style={{flexDirection: 'row'}}>
            <Text style={{fontWeight: 'bold'}}>Method: </Text>
            <Text>{method}</Text>
          </View>
          <View style={{flexDirection: 'row'}}>
            <Text style={{fontWeight: 'bold'}}>Notes: </Text>
            <Text numberOfLines={4} style={{flex: 1, textAlign: 'justify'}}>{notes}</Text>
          </View>
        </View>

      </TouchableOpacity>
    )
  }

  render() {
    const {person} = this.props.navigation.state.params;
    return (
      <View style={styles.container}>
        <Header
          title={person.name}
          showGoBack={true}
          onGoBackPress={() => this.props.navigation.goBack()}
        />
        <FlatList
          data={person.transactions}
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