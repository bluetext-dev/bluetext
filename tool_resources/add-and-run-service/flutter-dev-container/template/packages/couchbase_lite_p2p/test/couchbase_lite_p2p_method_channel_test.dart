import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:couchbase_lite_p2p/couchbase_lite_p2p_method_channel.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  MethodChannelCouchbaseLiteP2p platform = MethodChannelCouchbaseLiteP2p();
  const MethodChannel channel = MethodChannel('couchbase_lite_p2p');

  setUp(() {
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger.setMockMethodCallHandler(
      channel,
      (MethodCall methodCall) async {
        return '42';
      },
    );
  });

  tearDown(() {
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger.setMockMethodCallHandler(channel, null);
  });

  test('getPlatformVersion', () async {
    expect(await platform.getPlatformVersion(), '42');
  });
}
