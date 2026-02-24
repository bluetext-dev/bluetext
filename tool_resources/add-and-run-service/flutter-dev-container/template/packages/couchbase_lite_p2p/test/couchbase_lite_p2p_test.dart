import 'package:flutter_test/flutter_test.dart';
import 'package:couchbase_lite_p2p/couchbase_lite_p2p.dart';
import 'package:couchbase_lite_p2p/couchbase_lite_p2p_platform_interface.dart';
import 'package:couchbase_lite_p2p/couchbase_lite_p2p_method_channel.dart';
import 'package:plugin_platform_interface/plugin_platform_interface.dart';

class MockCouchbaseLiteP2pPlatform
    with MockPlatformInterfaceMixin
    implements CouchbaseLiteP2pPlatform {

  @override
  Future<String?> getPlatformVersion() => Future.value('42');
}

void main() {
  final CouchbaseLiteP2pPlatform initialPlatform = CouchbaseLiteP2pPlatform.instance;

  test('$MethodChannelCouchbaseLiteP2p is the default instance', () {
    expect(initialPlatform, isInstanceOf<MethodChannelCouchbaseLiteP2p>());
  });

  test('getPlatformVersion', () async {
    CouchbaseLiteP2p couchbaseLiteP2pPlugin = CouchbaseLiteP2p();
    MockCouchbaseLiteP2pPlatform fakePlatform = MockCouchbaseLiteP2pPlatform();
    CouchbaseLiteP2pPlatform.instance = fakePlatform;

    expect(await couchbaseLiteP2pPlugin.getPlatformVersion(), '42');
  });
}
