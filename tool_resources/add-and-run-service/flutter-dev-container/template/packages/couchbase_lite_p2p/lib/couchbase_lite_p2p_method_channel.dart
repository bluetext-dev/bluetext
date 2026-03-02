import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

import 'couchbase_lite_p2p_platform_interface.dart';

/// An implementation of [CouchbaseLiteP2pPlatform] that uses method channels.
class MethodChannelCouchbaseLiteP2p extends CouchbaseLiteP2pPlatform {
  /// The method channel used to interact with the native platform.
  @visibleForTesting
  final methodChannel = const MethodChannel('couchbase_lite_p2p');

  @override
  Future<String?> getPlatformVersion() async {
    final version = await methodChannel.invokeMethod<String>('getPlatformVersion');
    return version;
  }
}
