/**
 * Created by Yida Yin on 1/4/18
 */

import React from 'react';
import {
  Text,
  View,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';
import {inject, observer} from "mobx-react";
import ExpanableList from 'react-native-expandable-section-flatlist';
import Icon from 'react-native-vector-icons/FontAwesome';

import Header from '../components/Header';
import LambdaAPI from '../LambdaAPI';
import log from '../components/log';
import {timeConverter} from '../utils';


groupTransactionsByDate = (transactions) => {
  // sort transactions by UnixTimestamp
  transactions = transactions.sort(
    function(a, b) {
      return a.TransactionUnixTimestamp <= b.TransactionUnixTimestamp;
    });

  let groupedTransactions = {};
  for (let i = 0; i < transactions.length; i++) {
    const dateString = timeConverter(transactions[i].TransactionUnixTimestamp);
    transactions[i].dateString = dateString;
    if (dateString in groupedTransactions) {
      groupedTransactions[dateString].push(transactions[i]);
    } else {
      groupedTransactions[dateString] = [transactions[i]];
    }
  }
  // convert to expandable-section-flatlist format
  let groupedTransactionsList = [];
  for (let property in groupedTransactions) {
    if (groupedTransactions.hasOwnProperty(property)) {
      groupedTransactionsList.push({
        header: property,
        member: groupedTransactions[property]
      })
    }
  }
  return groupedTransactionsList;
};


@inject("store")
@observer
export default class TransactionListView extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      refreshing: false
    };
    this.fetchTransactions();
  }

  fetchTransactions() {
    const {email, token} = this.props.store;
    if (!email || !token) {
      return false;
    }
    LambdaAPI.getAllTransactions(email, token)
      .then((response) => {
        const respData = JSON.parse(response.data);
        this.props.store.transactions = respData.data;
        log.log(`${respData.count} transactions.`);
        log.log(respData);
        this.setState({refreshing: false});
      })
      .catch((error) => {
        log.log(`Call transactions, Failed! Status Code: ${error.status}. Error: `, error.response);
        this.setState({refreshing: false});
      })
  }

  _renderSection = (section, sectionId) => {
    return (
      <View style={{
        flexDirection: 'row',
        justifyContent: 'flex-start',
        backgroundColor: '#BBCCEE',
        height: 42,
        padding: 10,
        borderBottomWidth: 1,
        borderBottomColor: '#ddd'
      }}>
        <Text style={{fontWeight: 'bold', textAlign: 'center'}}>{section}</Text>
      </View>
    )
  };

  _renderRow = (rowItem, rowId, sectionId) => {
    return (
      <TouchableOpacity
        onPress={() => this.props.navigation.navigate('TransactionDetails', {item: rowItem})}
      >
        <View style={{
          backgroundColor: '#C1CEE6',
          borderBottomWidth: 1,
          borderBottomColor: '#ddd',
          paddingLeft: 15,
          padding: 5
        }}>
          <Text style={{fontWeight: 'bold'}}>{rowItem.FriendId}</Text>
          <Text>{rowItem.FriendName}</Text>
          <Text>{rowItem.TransactionPlatform}</Text>
        </View>
      </TouchableOpacity>
    )
  };

  _onRefreshing() {
    this.setState({refreshing: true});
    log.log("Refreshing Transactions......");
    this.fetchTransactions();
  }

  render() {
    const groupedTransactionsList = groupTransactionsByDate(this.props.store.transactions);

    return (
      <View style={styles.container}>
        <Header
          title='Transactions'
          rightItem={<Icon name={'gear'} size={26}/>}
        />

        <ExpanableList
          dataSource={groupedTransactionsList}
          headerKey="header"
          memberKey="member"
          renderRow={this._renderRow}
          renderSectionHeaderX={this._renderSection}

          refreshing={this.state.refreshing}
          onRefresh={this._onRefreshing.bind(this)}

          style={{width: "100%"}}
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