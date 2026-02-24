import Flutter
import UIKit
import CouchbaseLiteSwift

public class CouchbaseLiteP2pPlugin: NSObject, FlutterPlugin {
    private var channel: FlutterMethodChannel?
    private var database: Database?
    private var multipeerSyncManager: MultipeerSyncManager?
    private var replicator: Replicator?
    
    public static func register(with registrar: FlutterPluginRegistrar) {
        let channel = FlutterMethodChannel(name: "couchbase_lite_p2p", binaryMessenger: registrar.messenger())
        let instance = CouchbaseLiteP2pPlugin()
        instance.channel = channel
        registrar.addMethodCallDelegate(instance, channel: channel)
        instance.initializeCouchbase()
    }
    
    private func initializeCouchbase() {
        do {
            // Open Database
            let config = DatabaseConfiguration()
            database = try Database(name: "counter_db", config: config)
            
            // Initialize Sync Manager
            if let db = database {
                multipeerSyncManager = MultipeerSyncManager(database: db)
                
                // Listen for DB changes
                setupDatabaseListeners()
                
                // Listen for P2P status changes
                setupP2PListeners()
            }
        } catch {
            print("Error initializing Couchbase Lite: \(error)")
        }
    }
    
    private func setupDatabaseListeners() {
        guard let db = database else { return }
        
        do {
            let collection = try db.defaultCollection()
            _ = collection.addDocumentChangeListener(id: "counter") { [weak self] change in
                guard let self = self else { return }
                do {
                    if let doc = try collection.document(id: change.documentID) {
                        let count = doc.int(forKey: "count")
                        DispatchQueue.main.async {
                            self.channel?.invokeMethod("onCountChanged", arguments: count)
                        }
                    }
                } catch {
                    print("Error getting document: \(error)")
                }
            }
        } catch {
            print("Error setting up listener: \(error)")
        }
    }
    
    private func setupP2PListeners() {
        // TODO: Implement P2P status listener from MultipeerSyncManager
        // For now, we'll just poll or rely on manual updates if needed, 
        // but ideally MultipeerSyncManager should expose a callback/delegate.
        
        multipeerSyncManager?.onStatusChanged = { [weak self] status in
            DispatchQueue.main.async {
                self?.channel?.invokeMethod("onP2PStatusChanged", arguments: status)
            }
        }
    }

    public func handle(_ call: FlutterMethodCall, result: @escaping FlutterResult) {
        switch call.method {
        case "increment":
            incrementCounter(result: result)
        case "getCount":
            getCounter(result: result)
        case "startP2P":
            multipeerSyncManager?.start()
            result(true)
        case "getP2PStatus":
            if let status = multipeerSyncManager?.currentStatus {
                result(status)
            } else {
                result(["isRunning": false, "status": "Stopped"])
            }
        case "startSyncGatewayReplication":
            if let args = call.arguments as? [String: Any],
               let urlString = args["url"] as? String {
                startSyncGatewayReplication(urlString: urlString, result: result)
            } else {
                result(FlutterError(code: "INVALID_ARGS", message: "URL is required", details: nil))
            }
        default:
            result(FlutterMethodNotImplemented)
        }
    }
    
    private func startSyncGatewayReplication(urlString: String, result: @escaping FlutterResult) {
        guard let db = database else {
            result(FlutterError(code: "DB_ERROR", message: "Database not initialized", details: nil))
            return
        }
        
        guard let url = URL(string: urlString) else {
            result(FlutterError(code: "INVALID_URL", message: "Invalid URL: \(urlString)", details: nil))
            return
        }
        
        do {
            let target = URLEndpoint(url: url)
            var config = ReplicatorConfiguration(target: target)
            config.replicatorType = .pushAndPull
            config.continuous = true
            
            // Add default collection
            let collection = try db.defaultCollection()
            config.addCollection(collection, config: nil)
            
            replicator = Replicator(config: config)
            
            replicator?.addChangeListener { [weak self] change in
                guard let self = self else { return }
                let status = change.status
                var statusStr = "Stopped"
                switch status.activity {
                case .stopped: statusStr = "Stopped"
                case .offline: statusStr = "Offline"
                case .connecting: statusStr = "Connecting"
                case .idle: statusStr = "Idle"
                case .busy: statusStr = "Busy"
                @unknown default: statusStr = "Unknown"
                }
                
                var errorStr: String? = nil
                if let error = status.error {
                    errorStr = error.localizedDescription
                }
                
                DispatchQueue.main.async {
                    self.channel?.invokeMethod("onSyncGatewayStatusChanged", arguments: [
                        "status": statusStr,
                        "error": errorStr
                    ])
                }
            }
            
            replicator?.start()
            result(true)
        } catch {
            result(FlutterError(code: "REPLICATION_ERROR", message: error.localizedDescription, details: nil))
        }
    }
    
    private func incrementCounter(result: @escaping FlutterResult) {
        guard let db = database else {
            result(FlutterError(code: "DB_ERROR", message: "Database not initialized", details: nil))
            return
        }
        
        do {
            let collection = try db.defaultCollection()
            var newCount = 0
            
            try db.inBatch {
                var doc = try collection.document(id: "counter")?.toMutable()
                if doc == nil {
                    doc = MutableDocument(id: "counter")
                }
                
                if let doc = doc {
                    let count = doc.int(forKey: "count")
                    newCount = count + 1
                    doc.setInt(newCount, forKey: "count")
                    try collection.save(document: doc)
                }
            }
            result(newCount)
        } catch {
            result(FlutterError(code: "DB_ERROR", message: error.localizedDescription, details: nil))
        }
    }
    
    private func getCounter(result: @escaping FlutterResult) {
        guard let db = database else {
            result(0)
            return
        }
        
        do {
            let collection = try db.defaultCollection()
            if let doc = try collection.document(id: "counter") {
                result(doc.int(forKey: "count"))
            } else {
                result(0)
            }
        } catch {
            result(FlutterError(code: "DB_ERROR", message: error.localizedDescription, details: nil))
        }
    }
}
