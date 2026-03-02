package com.example.couchbase_lite_p2p.couchbase_lite_p2p

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import android.util.Log
import androidx.core.content.ContextCompat
import com.couchbase.lite.*
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.util.Calendar
import java.util.Date

class MultipeerSyncManager(
    private val context: Context,
    private val database: Database
) {
    
    private val peerGroupID = AppConfig.P2P_PEER_GROUP_ID
    private val identityLabel = AppConfig.P2P_IDENTITY_LABEL
    private val scope = CoroutineScope(Dispatchers.IO)
    
    companion object {
        private const val TAG = "MultipeerSync"
    }
    
    private var replicator: MultipeerReplicator? = null
    private var identity: TLSIdentity? = null
    
    data class P2PSyncState(
        val isRunning: Boolean = false,
        val myPeerID: String? = null,
        val connectedPeers: List<String> = emptyList(),
        val syncStatus: String = "Stopped",
        val error: String? = null
    )
    
    private val _syncState = MutableStateFlow(P2PSyncState())
    val syncState: StateFlow<P2PSyncState> = _syncState.asStateFlow()
    
    fun start() {
        scope.launch {
            try {
                if (_syncState.value.isRunning) return@launch
                
                if (!hasRequiredPermissions()) {
                    updateSyncState { it.copy(error = "Missing permissions") }
                    return@launch
                }
                
                // 1. Setup collections
                val collection = database.defaultCollection // Use default collection
                val collections = setOf(collection)
                
                // 2. Create or retrieve TLS identity
                identity = createOrRetrieveIdentity()
                
                // 3. Create authenticator
                val authenticator = MultipeerCertificateAuthenticator { _, _ -> true } // Accept all
                
                // 4. Create collection configurations
                val collectionConfigs = collections.map { 
                    MultipeerCollectionConfiguration.Builder(it).build() 
                }.toSet()
                
                // 5. Create MultipeerReplicator configuration
                val config = MultipeerReplicatorConfiguration.Builder()
                    .setPeerGroupID(peerGroupID)
                    .setIdentity(identity!!)
                    .setAuthenticator(authenticator)
                    .setCollections(collectionConfigs)
                    .build()
                
                // 6. Create MultipeerReplicator
                replicator = MultipeerReplicator(config)
                
                // 7. Set up listeners
                setupEventListeners()
                
                // 8. Start
                replicator?.start()
                
                val peerID = replicator?.peerId?.toString() ?: "unknown"
                updateSyncState { 
                    it.copy(isRunning = true, syncStatus = "Running", myPeerID = peerID, error = null) 
                }
                
                Log.i(TAG, "✅ MultipeerReplicator started with peer ID: $peerID")
                
            } catch (e: Exception) {
                Log.e(TAG, "❌ Failed to start MultipeerReplicator", e)
                updateSyncState { it.copy(isRunning = false, error = e.message) }
            }
        }
    }
    
    fun stop() {
        replicator?.stop()
        replicator = null
        updateSyncState { it.copy(isRunning = false, syncStatus = "Stopped", connectedPeers = emptyList()) }
    }
    
    private fun createOrRetrieveIdentity(): TLSIdentity {
        var identity = TLSIdentity.getIdentity(identityLabel)
        if (identity != null && identity.expiration.before(Date())) {
            TLSIdentity.deleteIdentity(identityLabel)
            identity = null
        }
        if (identity != null) return identity
        
        val certAttributes = mapOf(
            TLSIdentity.CERT_ATTRIBUTE_COMMON_NAME to "CounterApp",
            TLSIdentity.CERT_ATTRIBUTE_ORGANIZATION to "Couchbase Demo"
        )
        
        val calendar = Calendar.getInstance()
        calendar.add(Calendar.YEAR, 1)
        
        return TLSIdentity.createIdentity(
            setOf(KeyUsage.CLIENT_AUTH, KeyUsage.SERVER_AUTH),
            certAttributes,
            calendar.time,
            identityLabel
        )
    }
    
    private fun setupEventListeners() {
        val repl = replicator ?: return
        
        repl.addStatusListener { status ->
            scope.launch {
                updateSyncState { it.copy(isRunning = status.isActive) }
            }
        }
        
        repl.addPeerDiscoveryStatusListener { status ->
            scope.launch {
                val currentPeers = _syncState.value.connectedPeers.toMutableList()
                val peerIdStr = status.peer.toString()
                
                if (status.isOnline) {
                    if (!currentPeers.contains(peerIdStr)) currentPeers.add(peerIdStr)
                } else {
                    currentPeers.remove(peerIdStr)
                }
                
                updateSyncState { it.copy(connectedPeers = currentPeers) }
            }
        }
    }
    
    private fun updateSyncState(update: (P2PSyncState) -> P2PSyncState) {
        _syncState.value = update(_syncState.value)
    }
    
    private fun hasRequiredPermissions(): Boolean {
        val permissions = mutableListOf<String>()
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions.add(Manifest.permission.NEARBY_WIFI_DEVICES)
        } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            permissions.add(Manifest.permission.BLUETOOTH_ADVERTISE)
            permissions.add(Manifest.permission.BLUETOOTH_CONNECT)
            permissions.add(Manifest.permission.BLUETOOTH_SCAN)
            permissions.add(Manifest.permission.ACCESS_FINE_LOCATION)
        } else {
            permissions.add(Manifest.permission.ACCESS_FINE_LOCATION)
        }
        
        return permissions.all {
            ContextCompat.checkSelfPermission(context, it) == PackageManager.PERMISSION_GRANTED
        }
    }
}
