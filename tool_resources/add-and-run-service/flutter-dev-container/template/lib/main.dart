import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:couchbase_lite_p2p/couchbase_lite_p2p.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const MyHomePage(title: 'Flutter Couchbase Lite Demo'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  final _couchbaseLiteP2p = CouchbaseLiteP2p();
  
  int _counter = 0;
  String _p2pStatus = 'Stopped';
  String? _p2pError;
  int _connectedPeers = 0;
  String _myPeerID = '';
  bool _isP2PRunning = false;
  
  // Sync Gateway Status
  String _syncGatewayStatus = 'Stopped';
  String? _syncGatewayError;

  @override
  void initState() {
    super.initState();
    _initListeners();
    _loadCounter();
    _requestPermissionsAndStartP2P();
    _startNativeReplication();
  }
  
  Future<void> _startNativeReplication() async {
    try {
      // Use 10.0.2.2 for Android Emulator to reach host localhost
      // Use 192.168.86.142 for physical device (Mac IP)
      String url = 'ws://192.168.86.142:4984/main';
      if (Platform.isAndroid) {
        // Assuming Android Emulator
        url = 'ws://10.0.2.2:4984/main';
      }
      
      await _couchbaseLiteP2p.startSyncGatewayReplication(url);
      debugPrint("Native Sync Gateway Replication started");
    } catch (e) {
      debugPrint("Failed to start Native replication: $e");
      setState(() {
        _syncGatewayStatus = 'Error';
        _syncGatewayError = e.toString();
      });
    }
  }

  @override
  void dispose() {
    _couchbaseLiteP2p.dispose();
    super.dispose();
  }

  Future<void> _requestPermissionsAndStartP2P() async {
    // Request permissions
    Map<Permission, PermissionStatus> statuses = await [
      Permission.location,
      Permission.bluetooth,
      Permission.bluetoothScan,
      Permission.bluetoothAdvertise,
      Permission.bluetoothConnect,
      Permission.nearbyWifiDevices,
    ].request();

    // Check if all granted (or at least the critical ones)
    // For simplicity, we just try to start P2P. The native side checks permissions too.
    _startP2P();
  }

  void _initListeners() {
    _couchbaseLiteP2p.onCountChanged.listen((count) {
      setState(() {
        _counter = count;
      });
    });

    _couchbaseLiteP2p.onP2PStatusChanged.listen((status) {
      setState(() {
        _isP2PRunning = status['isRunning'] as bool;
        _myPeerID = status['myPeerID'] as String;
        _connectedPeers = status['connectedPeers'] as int;
        _p2pStatus = status['status'] as String;
        if (status['error'] != null) {
          _p2pError = status['error'] as String;
        } else {
          _p2pError = null;
        }
      });
    });

    _couchbaseLiteP2p.onSyncGatewayStatusChanged.listen((status) {
      setState(() {
        _syncGatewayStatus = status['status'] as String;
        if (status['error'] != null) {
          _syncGatewayError = status['error'] as String;
        } else {
          _syncGatewayError = null;
        }
      });
    });
  }

  Future<void> _loadCounter() async {
    try {
      final int result = await _couchbaseLiteP2p.getCount();
      setState(() {
        _counter = result;
      });
    } on PlatformException catch (e) {
      debugPrint("Failed to get count: '${e.message}'.");
    }
  }

  Future<void> _startP2P() async {
    try {
      await _couchbaseLiteP2p.startP2P();
    } on PlatformException catch (e) {
      debugPrint("Failed to start P2P: '${e.message}'.");
    }
  }

  Future<void> _incrementCounter() async {
    try {
      final int result = await _couchbaseLiteP2p.increment();
      setState(() {
        _counter = result;
      });
    } on PlatformException catch (pe) {
      debugPrint("Failed to increment native: '${pe.message}'.");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            const Text(
              'You have pushed the button this many times (persisted in Couchbase Lite):',
            ),
            Text(
              '$_counter',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 20),
            Card(
              margin: const EdgeInsets.all(16),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    Text('Mesh Sync Status', style: Theme.of(context).textTheme.titleMedium),
                    const SizedBox(height: 8),
                    Text('Status: $_p2pStatus'),
                    if (_p2pError != null)
                      Text('Error: $_p2pError', style: const TextStyle(color: Colors.red)),
                    Text('My Peer ID: $_myPeerID'),
                    Text('Connected Peers: $_connectedPeers'),
                  ],
                ),
              ),
            ),
            Card(
              margin: const EdgeInsets.all(16),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    Text('Sync Gateway Status', style: Theme.of(context).textTheme.titleMedium),
                    const SizedBox(height: 8),
                    Text('Status: $_syncGatewayStatus'),
                    if (_syncGatewayError != null)
                      Text('Error: $_syncGatewayError', style: const TextStyle(color: Colors.red)),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _incrementCounter,
        tooltip: 'Increment',
        child: const Icon(Icons.add),
      ),
    );
  }
}
