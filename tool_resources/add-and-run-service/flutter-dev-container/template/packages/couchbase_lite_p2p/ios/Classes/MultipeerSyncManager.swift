import Foundation
import CouchbaseLiteSwift

class MultipeerSyncManager {
    private let database: Database
    private let peerGroupID = "com.example.counterapp"
    private let identityLabel = "com.example.counterapp.p2p.identity"
    
    var onStatusChanged: (([String: Any]) -> Void)?
    
    private var replicator: MultipeerReplicator?
    private var identity: TLSIdentity?
    
    private var isRunning = false
    private var connectedPeers: [PeerID] = []
    private var syncStatus = "Stopped"
    private var lastError: String?
    
    init(database: Database) {
        self.database = database
    }
    
    var currentStatus: [String: Any] {
        var peerIDStr = "unknown"
        if let pid = replicator?.peerID {
            peerIDStr = "\(pid)"
        }
        
        var status: [String: Any] = [
            "isRunning": isRunning,
            "myPeerID": peerIDStr,
            "connectedPeers": connectedPeers.count,
            "status": syncStatus
        ]
        
        if let error = lastError {
            status["error"] = error
        }
        
        return status
    }
    
    func start() {
        if isRunning { return }
        
        // Use a Task to handle async identity creation
        Task {
            do {
                // Add a small delay to ensure DB is fully ready and avoid race conditions
                try await Task.sleep(nanoseconds: 500_000_000) // 0.5 seconds

                // 1. Create or retrieve TLS identity
                identity = try createOrRetrieveIdentity()
                
                // 2. Create authenticator (accept all)
                let authenticator = MultipeerCertificateAuthenticator { _, _ in true }
                
                // 3. Create collection configurations
                let collection = try database.defaultCollection()
                let config = MultipeerCollectionConfiguration(collection: collection)
                
                // 4. Create MultipeerReplicator configuration
                let replConfig = MultipeerReplicatorConfiguration(
                    peerGroupID: peerGroupID,
                    identity: identity!,
                    authenticator: authenticator,
                    collections: [config]
                )
                
                // Attempt to force service type using KVC (desperate measure)
                // If this crashes, we know the property doesn't exist.
                // But if it works, it fixes the NoAuth error.
                // Note: serviceType usually doesn't include the underscore prefix in the setter
                // but Info.plist needs it.
                // Try "cbl-p2p" which matches _cbl-p2p._tcp
                // replConfig.setValue("cbl-p2p", forKey: "serviceType") 
                
                // 5. Create MultipeerReplicator
                replicator = try MultipeerReplicator(config: replConfig)
                
                // 6. Set up listeners
                setupEventListeners()
                
                // 7. Start
                replicator?.start()
                
                // 8. Update state
                isRunning = true
                syncStatus = "Running"
                notifyStatusChanged()
                
                print("✅ MultipeerReplicator started")
                
            } catch {
                print("❌ Failed to start MultipeerReplicator: \(error)")
                syncStatus = "Error: \(error.localizedDescription)"
                notifyStatusChanged()
            }
        }
    }
    
    func stop() {
        if !isRunning { return }
        
        replicator?.stop()
        replicator = nil
        
        isRunning = false
        syncStatus = "Stopped"
        connectedPeers.removeAll()
        notifyStatusChanged()
        
        print("🛑 MultipeerReplicator stopped")
    }
    
    private func createOrRetrieveIdentity() throws -> TLSIdentity {
        if let existing = try? TLSIdentity.identity(withLabel: identityLabel) {
            if existing.expiration > Date() {
                return existing
            }
            try? TLSIdentity.deleteIdentity(withLabel: identityLabel)
        }
        
        let attrs: [String: String] = [certAttrCommonName: "CounterApp"]
        let expiration = Calendar.current.date(byAdding: .year, value: 1, to: Date())!
        
        return try TLSIdentity.createIdentity(
            for: [.clientAuth, .serverAuth],
            attributes: attrs,
            expiration: expiration,
            label: identityLabel
        )
    }
    
    private func setupEventListeners() {
        guard let replicator = replicator else { return }
        
        // Status Listener
        _ = replicator.addStatusListener { [weak self] status in
            guard let self = self else { return }
            self.isRunning = status.active
            self.syncStatus = status.active ? "Active" : "Inactive"
            if let error = status.error {
                print("❌ Multipeer Replicator error: \(error.localizedDescription)")
                self.lastError = error.localizedDescription
            } else {
                self.lastError = nil
            }
            self.notifyStatusChanged()
        }
        
        // Peer Discovery Listener
        _ = replicator.addPeerDiscoveryStatusListener { [weak self] status in
            guard let self = self else { return }
            if status.online {
                if !self.connectedPeers.contains(status.peerID) {
                    self.connectedPeers.append(status.peerID)
                }
            } else {
                self.connectedPeers.removeAll { $0 == status.peerID }
            }
            self.notifyStatusChanged()
        }
    }
    
    private func notifyStatusChanged() {
        onStatusChanged?(currentStatus)
    }
}
