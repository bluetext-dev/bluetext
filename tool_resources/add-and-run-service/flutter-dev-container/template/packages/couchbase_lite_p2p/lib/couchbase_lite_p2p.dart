import 'dart:async';
import 'package:flutter/services.dart';

class CouchbaseLiteP2p {
  static const MethodChannel _channel = MethodChannel('couchbase_lite_p2p');

  final StreamController<int> _countController = StreamController<int>.broadcast();
  final StreamController<Map<String, dynamic>> _p2pStatusController = StreamController<Map<String, dynamic>>.broadcast();
  final StreamController<Map<String, dynamic>> _syncGatewayStatusController = StreamController<Map<String, dynamic>>.broadcast();

  Stream<int> get onCountChanged => _countController.stream;
  Stream<Map<String, dynamic>> get onP2PStatusChanged => _p2pStatusController.stream;
  Stream<Map<String, dynamic>> get onSyncGatewayStatusChanged => _syncGatewayStatusController.stream;

  CouchbaseLiteP2p() {
    _channel.setMethodCallHandler(_handleMethodCall);
  }

  Future<dynamic> _handleMethodCall(MethodCall call) async {
    switch (call.method) {
      case 'onCountChanged':
        _countController.add(call.arguments as int);
        break;
      case 'onP2PStatusChanged':
        _p2pStatusController.add(Map<String, dynamic>.from(call.arguments as Map));
        break;
      case 'onSyncGatewayStatusChanged':
        _syncGatewayStatusController.add(Map<String, dynamic>.from(call.arguments as Map));
        break;
    }
  }

  Future<int> increment() async {
    final int result = await _channel.invokeMethod('increment');
    return result;
  }

  Future<int> getCount() async {
    final int result = await _channel.invokeMethod('getCount');
    return result;
  }

  Future<bool> startP2P() async {
    final bool result = await _channel.invokeMethod('startP2P');
    return result;
  }

  Future<Map<String, dynamic>> getP2PStatus() async {
    final Map<dynamic, dynamic> result = await _channel.invokeMethod('getP2PStatus');
    return Map<String, dynamic>.from(result);
  }

  Future<bool> startSyncGatewayReplication(String url) async {
    final bool result = await _channel.invokeMethod('startSyncGatewayReplication', {'url': url});
    return result;
  }
  
  void dispose() {
    _countController.close();
    _p2pStatusController.close();
    _syncGatewayStatusController.close();
  }
}
