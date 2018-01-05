/**
 * Created by Yida Yin on 1/4/18
 */

import React from 'react';
import {Button, StyleSheet, Text, View} from 'react-native';
import {AuthSession} from 'expo';

import LambdaAPI from '../LambdaAPI';


const CLIENT_ID = '1420c3c4-8202-411f-870d-64b6166fd980';

export default class LoginPage extends React.Component {
  state = {
    oauthResult: null,
    lambdaResult: null,
  };

  _handlePressAsync = async () => {
    let redirectUrl = AuthSession.getRedirectUrl();
    const authURL =
      `https://login.microsoftonline.com/common/oauth2/v2.0/authorize?` +
      `scope=openid+User.Read+Mail.Read` +
      `&response_type=code` +
      `&client_id=${encodeURIComponent(CLIENT_ID)}` +
      `&redirect_uri=${encodeURIComponent(redirectUrl)}`;
    console.log("Outlook OAuth URL: ", authURL);
    let result = await AuthSession.startAsync({
      authUrl: authURL
    });
    console.log(result);
    this.setState({oauthResult: result});

    if (result && result.type === 'success') {
      const code = result.params.code;
      console.log("Authorized successfully, code: ", code);
      LambdaAPI.uploadOutlookCode(code)
        .then((response) => {
          console.log(response);
          this.setState({lambdaResult: response.data});
        })
        .catch((error) => {
          console.log(error);
          this.setState({lambdaResult: error.data});
        })
    }
  };

  render() {
    return (
      <View style={styles.container}>
        <Button title="Open Outlook Auth" onPress={this._handlePressAsync}/>
        <Button title="Open Transaction List View" onPress={() => this.props.navigation.navigate('TransactionListView')}/>
        {this.state.oauthResult ? (
          <Text>{JSON.stringify(this.state.oauthResult)}</Text>
        ) : null}
        {this.state.lambdaResult ? (
          <Text>{JSON.stringify(this.state.lambdaResult)}</Text>
        ) : null}
      </View>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
});