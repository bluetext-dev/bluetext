import 'package:plugin_platform_interface/plugin_platform_interface.dart';

import 'couchbase_lite_p2p_method_channel.dart';

abstract class CouchbaseLiteP2pPlatform extends PlatformInterface {
  /// Constructs a CouchbaseLiteP2pPlatform.
  CouchbaseLiteP2pPlatform() : super(token: _token);

  static final Object _token = Object();

  static CouchbaseLiteP2pPlatform _instance = MethodChannelCouchbaseLiteP2p();

  /// The default instance of [CouchbaseLiteP2pPlatform] to use.
  ///
  /// Defaults to [MethodChannelCouchbaseLiteP2p].
  static CouchbaseLiteP2pPlatform get instance => _instance;

  /// Platform-specific implementations should set this with their own
  /// platform-specific class that extends [CouchbaseLiteP2pPlatform] when
  /// they register themselves.
  static set instance(CouchbaseLiteP2pPlatform instance) {
    PlatformInterface.verifyToken(instance, _token);
    _instance = instance;
  }

  Future<String?> getPlatformVersion() {
    throw UnimplementedError('platformVersion() has not been implemented.');
  }
}
